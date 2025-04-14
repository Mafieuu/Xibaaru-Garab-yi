//  ***************************************************************
//  Ce script est a executer dans google eath engine, remplacer le nom de chaque geometrie pour correspondre a ce que vous avez creez 
//  dans la plateforme.
//
// *********************************************************************

var geometry = /* color: #ff0000 */ee.Geometry.MultiPolygon(        [[[[-17.085890998848857, 14.78492669453916],           [-17.08408855439085, 14.777084103533461],           [-17.076664199837627, 14.783806341738117]]],         [[[-17.07387470246214, 14.781524123704346],           [-17.073273887642802, 14.777457566670375],           [-17.069926490792216, 14.77828748245337],           [-17.0718147659387, 14.782478508709506]]]]),    home =     /* color: #00ff00 */    /* displayProperties: [      {        "type": "rectangle"      }    ] */    ee.Geometry.Polygon(        [[[-17.063145866402568, 14.784968188976304],          [-17.063145866402568, 14.779075899509849],          [-17.055506935128154, 14.779075899509849],          [-17.055506935128154, 14.784968188976304]]], null, false),    gestion = /* color: #0000ff */ee.Geometry.MultiPolygon(        [[[[-17.04932712555784, 14.783972320295687],           [-17.05288909912962, 14.776337175333259],           [-17.03859828949827, 14.786627959958416]]],         [[[-17.047481765755595, 14.788619668384106],           [-17.05284618378538, 14.788702655838547],           [-17.052245368966044, 14.785715087488738]]],         [[[-17.04061531067747, 14.776171190939978],           [-17.04336189270872, 14.77886842161457],           [-17.046451797493877, 14.775382763339822],           [-17.043533554085673, 14.776876623735486],           [-17.042932739266337, 14.775258274509795],           [-17.042718162545146, 14.776254183152464],           [-17.04108737946409, 14.77567323699912]]]]);

//exporter la geometri 'geometry'
Export.table.toDrive({
  collection: ee.FeatureCollection([geometry]),
  description: 'geometry_export',
  fileFormat: 'GeoJSON',
  folder: 'GEE_Exports', 
  fileNamePrefix: 'geometry'
});

//exporter la geometri 'home'
Export.table.toDrive({
  collection: ee.FeatureCollection([home]),
  description: 'home_export',
  fileFormat: 'GeoJSON',
  folder: 'GEE_Exports',
  fileNamePrefix: 'home'
});


//exporter la geometri'gestion'
Export.table.toDrive({
  collection: ee.FeatureCollection([gestion]),
  description: 'gestion_export',
  fileFormat: 'GeoJSON',
  folder: 'GEE_Exports',
  fileNamePrefix: 'gestion'
});
