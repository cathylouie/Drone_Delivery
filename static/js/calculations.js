function arrayOfx(a){

	var xlist = [];
	for (var i = 0; i < a.length; i++){
	//change lng to x co-ordinate of nodes in the grid
	if ((((-ulc[1])-a[i])*1000000)%100 !== 0){
		var x = parseInt(((-ulc[1])-a[i])*1000000/100); 
 		}
	else
 		{x = ((-ulc[1])-a[i])*1000000/100;
 		}
	xlist.push(x);
	}
	return xlist;
}

function arrayOfy(b){

			var ylist = [];
			for (var i = 0; i < b.length; i++){	
			//change lat to y co-ordinate of nodes in the grid
			if (((ulc[0]-b[i])*1000000)%100 !== 0){
		 		var y = parseInt((ulc[0]-b[i])*1000000/100); 
		 		}
			else
		 		{y = (ulc[0]-b[i])*1000000/100;
		 		}
			ylist.push(y); 	
			}
			return ylist;
		}

function setUnWalkable(xlist, e, ylist, g){

        	for (var i = 0; i < xlist.length; i++)
        	{
        		for (var j = 0; j < e.length; j++)
        		{	
        			grid.setWalkableAt(xlist[i]+e[j], ylist[i]+g[j], false);
        		}
        	}
        	return grid;
        }

function lngTox(lng){

        	var lng = -(lng);
        	console.log(lng);//keeping for debugging
			if ((((-ulc[1])-lng)*1000000)%100 !== 0){
			var x1 = parseInt(((-ulc[1])-lng)*1000000/100); 
			}
			else
			{x1 = ((-ulc[1])-lng)*1000000/100;
			}
			return x1;
		}

function latToy(lat){

			if (((ulc[0]-lat)*1000000)%100 !== 0){
			var y1 = parseInt((ulc[0]-lat)*1000000/100); 
			}
			else
			{y1 = (ulc[0]-lat)*1000000/100;
			}
			return y1;
		}

function latLngFromPath(path){

			var line_points = [];
				for (var i = 0; i < path.length; i++){
					var p = [(ulc[0] - path[i][1]*1/10000), - ((-ulc[1]) - path[i][0]*1/10000).toFixed(6)];

					line_points.push(p);
					}
					return line_points;
				}

function geoJsonFromPath(path){

			var geojson = { type: 'LineString', coordinates: []};

			for (var i = 0; i < path.length; i++){
			var p = [ - ((-ulc[1]) - path[i][0]*1/10000).toFixed(6), (ulc[0] - path[i][1]*1/10000)]    
			geojson.coordinates.push(p);
			}
			return geojson;
		}

