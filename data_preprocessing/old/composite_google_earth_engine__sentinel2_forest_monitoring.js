// ====================== Image composite ===========================================================
//
// Permet de charger et traiter des images de sentinel2-level 2A (image corrige sur diffusion et absorption de lumiere)
// On se donne une plage de date et on traite tous les images disponible en filtrant puis recomposer pour avoir
// la meilleur qualite d'image d'une période donnée.
// 


var region = ee.Geometry.Polygon([
    [[-16.75073726530263, 12.935246118519657],
    [-16.751305893613786, 12.929139402451897],
    [-16.733560398771257, 12.929850466119884],
    [-16.73424704427907, 12.937713858633533]]
  ]);
  

  var startDate = '2023-01-01';
  var endDate = '2024-12-31';
  
 
  var sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(startDate, endDate)
    .filterBounds(region)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)); // mois de  20% de nuages
  
  //  Fonction pour masquer les nuages 
  function maskS2clouds(image) {
    // Utiliser SCL (Scene Classification Layer) pour masquer les nuages
    // Cette bande contient une classification de chaque pixel
    var scl = image.select('SCL');
    // Exclure les pixels indésirables
    var validPixels = scl.neq(1)  // sature/defectueux
                      .and(scl.neq(3)) // ombre
                      .and(scl.neq(7)) // nuage faible prob.
                      .and(scl.neq(8)) // nuage moyen prob.
                      .and(scl.neq(9)) // nuage fort prob.
                      .and(scl.neq(10)); // cirrus
    
    // Utiliser la bande MSK_CLDPRB  (Cloud Probability Mask) pour masquer les nuages
    // Cette bande fournit une probabilité en pourcentage pour chaque pixel d'être un nuage.
    // noter que ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20) accepte une image avec 20% de taux de nuage 
    // alors que MSK_CLDPRB opére sur chaque pixel

    var cloudProb = image.select('MSK_CLDPRB');
    var cloudMask = cloudProb.lt(20); // Pixels avec moins de 20% de probabilité de nuage
    
    // Combiner les masques
    var finalMask = validPixels.and(cloudMask);
    
    // Appliquer le masque et  normaliser la  réflectance
    return image.updateMask(finalMask).divide(10000);
  }
  // appel de la fonction pour masquer les elements indesirables
  var sentinel2_masked = sentinel2.map(maskS2clouds);

  //La réflectance est une mesure de la quantité de lumière qu'une surface renvoie après avoir été éclairée. 
  // Elle est exprimée sous forme de fraction ou de pourcentage : une réflectance de 0.3 signifie que 30% de la lumière incidente est réfléchie.

 
  var bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'];
  var sentinel2_viz = sentinel2_masked.select(bands);
  
  // Combiner plusieurs images d'une période donnée en une seule image représentative
  // L'utilisation de la médiane permet de réduire l'impact des valeurs aberrantes comme les nuages résiduels
  // et de créer une image plus stable

  var composite = sentinel2_viz.median().clip(region);
  
  // Visualisation 

  var trueColorVis = {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.35}; // augmenter la réflectance (>0.3) rend les objets trop brilliants
  Map.centerObject(region, 10); // Centrer la carte sur votre région
  Map.addLayer(composite, trueColorVis, 'Sentinel-2 True Color');
  // Si on augmentes max :05 Les pixels qui réfléchissent plus de lumière comme le sol nu, les toits, les nuages seront mieux visibles,
  //  mais l’image peut paraître plus brillante.
  // Si tu mets max = 1, tout sera affiché avec sa réflectance d'origine,
  //  mais l'image pourrait devenir trop sombre puisque les valeurs naturelles (sol, végétation) sont souvent bien inférieures à 1.
  
 
  var nirVis = {bands: ['B8', 'B4', 'B3'], min: 0, max: 0.5};// Les plantes réfléchissent beaucoup d'infrarouge
  // la végétation apparaît en rouge vif car elle réfléchit fortement le proche infrarouge

  Map.addLayer(composite, nirVis, 'Sentinel-2 NIR');
  
  var swirVis = {bands: ['B11', 'B8', 'B4'], min: 0, max: 0.5};
  Map.addLayer(composite, swirVis, 'Sentinel-2 SWIR');
  // Permet de distinguer différents types de végétation, l'humidité du sol et les zones brûlées
  
  var ndvi = composite.normalizedDifference(['B8', 'B4']);
  var ndviVis = {palette: ['red', 'yellow', 'green'], min: 0, max: 1};
  // du rouge pour les valeurs faibles au vert pour les valeurs élevées
  Map.addLayer(ndvi, ndviVis, 'NDVI');
  