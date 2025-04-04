// ====================== Image mono date ===========================================================
//
//charge des images Sentinel-2 Level 2A (avec correction atmosphérique) pour une période donnée et sur une région d'intérêt.
// Il applique ensuite un masquage des nuages en combinant deux approches 
// : l'utilisation du SCL (Scene Classification Layer) 
// et de la bande de probabilité de nuages (issue de la collection S2_CLOUD_PROBABILITY). 
// Après avoir masqué les pixels indésirables, le script sélectionne l'image ayant le moins de nuages (une image "monodate") 
// et l'affiche en vraies couleurs, en infrarouge proche, en SWIR et avec l'indice NDVI.


var startDate = '2025-03-01';  
var endDate = '2025-03-31';    


var cloudCoverageMax = 10;     // fixe le pourcentage maximal de nuages autorisé par image
var cloudProbabilityThreshold = 15; //  le seuil de probabilité par pixel en pourcentage utilisé pour masquer les nuages

var trueColorMax = 0.3;        // Valeur maximale de réflectance pour la visualisation en vraie couleur
var nirMax = 0.5;              // Valeur maximale pour la visualisation en proche infrarouge 
var swirMax = 0.5;             // Valeur maximale pour la visualisation en SWIR
var ndviMin = 0;               // Valeur minimale pour la visualisation NDVI
var ndviMax = 0.8;             // Valeur maximale pour la visualisation NDVI
var zoomLevel = 15;            //  le niveau de zoom pour centrer la carte

var region = ee.Geometry.Polygon([
  [[-16.75073726530263, 12.935246118519657],
   [-16.751305893613786, 12.929139402451897],
   [-16.733560398771257, 12.929850466119884],
   [-16.73424704427907, 12.937713858633533]]
]);

// ====================== Chargement et préparation des collections ============================================

// Charger la collection Sentinel-2 Level 2A  avec les filtres
var s2_sr = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterDate(startDate, endDate)
  .filterBounds(region)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloudCoverageMax));        //Filtrage par taux de nuages global 

// Charger la collection de probabilité de nuages Sentinel-2
var s2_cloudProb = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY') //  fournit une estimation par pixel en pourcentage de la présence de nuages
  .filterDate(startDate, endDate)
  .filterBounds(region);

// Joindre les deux collections 
// Cette opération associe à chaque image de s2_sr,
//  l'image correspondante de la collection s2_cloudProb
var s2_joined = ee.Join.saveFirst('cloud_prob').apply({
  primary: s2_sr,
  secondary: s2_cloudProb,
  condition: ee.Filter.equals({
    leftField: 'system:index',
    rightField: 'system:index'
  })
});
s2_joined = ee.ImageCollection(s2_joined);

// ====================== Fonction de masquage des nuages ============================================

//  nettoyer chaque image en supprimant les pixels indésirables 
// avant de choisir l'image la meilleure parmi toutes celles disponibles sur la période.


// Ici, on utilise le SCL pour exclure certains pixels (saturés, ombres, nuages avec probabilité moyenne à forte, défectueux )
// Puis, on récupère la bande 'probability' provenant l'image joint et on ne garde que les pixels dont
// la probabilité est inférieure au seuil cloudProbabilityThreshold 
function maskS2clouds(image) {
  // Masquage basé sur SCL
  var scl = image.select('SCL');
  var validPixels = scl.neq(1)  // pixels saturés/défectueux
                    .and(scl.neq(3)) // ombres
                    // Note : la valeur 7 correspond à "non classifié", une piste a creuser
                    .and(scl.neq(8)) // nuages probabilité moyenne
                    .and(scl.neq(9)) // nuages (probabilité forte
                    .and(scl.neq(10)); // cirrus (des nuages atypique)
  
  // Récupérer la bande de probabilité de nuages depuis la collection jointe
  var cloudProb = ee.Image(image.get('cloud_prob')).select('probability');
  var cloudMask = cloudProb.lt(cloudProbabilityThreshold);
  
  // Combiner les deux masques
  var finalMask = validPixels.and(cloudMask);
  
  // Appliquer le masque et normaliser la réflectance
  return image.updateMask(finalMask).divide(10000);
}

// Appliquer la fonction de masquage à la collection jointe
var sentinel2_masked = s2_joined.map(maskS2clouds);


var bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'];
var sentinel2_viz = sentinel2_masked.select(bands);

//  sélectionne l'image individuelle qui présente le moins de nuages et de perturbations
var sortedImages = sentinel2_viz.sort('CLOUDY_PIXEL_PERCENTAGE');
var bestImage = ee.Image(sortedImages.first()).clip(region);

// Afficher la date de l'image sélectionnée (pour information)
var indexValue = ee.String(bestImage.get('system:index'));
var dateString = indexValue.slice(0, 8);
var formattedDate = ee.Date.parse('yyyyMMdd', dateString).format('YYYY-MM-dd');
print("Date de l'image :", formattedDate);

// ====================== Visualisation de l'image monodate ==================================================

Map.centerObject(region, zoomLevel);


var trueColorVis = {bands: ['B4', 'B3', 'B2'], min: 0, max: trueColorMax};
Map.addLayer(bestImage, trueColorVis, 'Image Monodate - Vraie Couleur');

// NIR
var nirVis = {bands: ['B8', 'B4', 'B3'], min: 0, max: nirMax};
Map.addLayer(bestImage, nirVis, 'Image Monodate - NIR', false);

// SWIR
var swirVis = {bands: ['B11', 'B8', 'B4'], min: 0, max: swirMax};
Map.addLayer(bestImage, swirVis, 'Image Monodate - SWIR', false);

// NDVI
var ndvi = bestImage.normalizedDifference(['B8', 'B4']);
var ndviVis = {palette: ['red', 'yellow', 'green'], min: ndviMin, max: ndviMax};
// du rouge pour les valeurs faibles au vert pour les valeurs élevées
Map.addLayer(ndvi, ndviVis, 'Image Monodate - NDVI', false);

// Ajout de contour 
Map.addLayer(ee.Image().paint(region, 1, 2), {palette: 'red'}, 'Contour de la région');
