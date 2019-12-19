<!DOCTYPE html>
<html>
	<head>
		<style type="text/css">
			#myCanvas {
				position: absolute;
				top: 0px;
				left: 0px;
			}
		</style>
		<script src="three.min.js"></script>
		<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>
		<script type="text/javascript">

			function len(arr) {
				return Object.keys(arr).length
			}

			function resizeCanvas() {
				var c = $('#myCanvas');
				var ct = c.get(0).getContext('2d');
				var container = $(c).parent();

				c.attr('width',  $( window ).width() ); //max width = screen.availWidth
				c.attr('height', $( window ).height() ); //max height
			}

			$( window ).resize(function() {
				resizeCanvas();
			});

			$(document).ready(function(){
				//$('.plwid').animate({ left: '+=120' }, 400 );
				var stars = {}
				var serial = 0;
				var maxStars = 130;

				resizeCanvas();
				
				function generateStars() {
					if (len(stars) < maxStars) {
						//var xPos = Math.floor(Math.random() * 299)
						var yPos = Math.floor(Math.random() * $(window).height())
						var updateIntv = 100-Math.floor(Math.random() * 90)
						var updateSpeed = (2+(Math.random()*2)) - (updateIntv/100)
						var tailLen = (100/4)*updateSpeed

						console.log(serial + ' will have ' + updateSpeed + 'px per ' + updateIntv + 'msec')

						stars[serial] = {x: 0, y: yPos, update: updateSpeed, updateInterval: updateIntv, color: 'white', tailLength: tailLen, lastUpdate: (new Date()).getTime()}
						serial++;
						serial=serial%maxStars;
					}
					setTimeout(function() {
						generateStars();
					}, 1000);
				}

				/*
				0 will have 2.906690375180915px per 37msec
				1 will have 3.743592446204275px per 26msec
				2 will have 4.06892914744094px per 64msec
				*/

				function drawStars() {
					// Get the canvas element.
					canvas = document.getElementById("myCanvas");

					// Make sure you got it.
					if (canvas.getContext) {
						// Specify 2d canvas type.
						ctx = canvas.getContext("2d");

						// Paint it black.
						ctx.fillStyle = "black";
						ctx.rect(0, 0, canvas.width, canvas.height);
						ctx.fill();

						var currTime = (new Date()).getTime();

						for (var key in stars) {
							if (currTime-stars[key].lastUpdate > stars[key].updateInterval) {

								stars[key].x = stars[key].x+stars[key].update

								if (stars[key].x > canvas.width+tail) {
									delete stars[key];
									continue;
								}
								stars[key].lastUpdate = currTime;
							}
							
							x = stars[key].x;
							y = stars[key].y;
							tail = stars[key].tailLength;

							ctx.fillStyle = "white";
							ctx.beginPath();
							ctx.arc(x, y+0.5, 0.7, 0, Math.PI * 2, true);
							ctx.closePath();
							ctx.fill();

							var gradient=ctx.createLinearGradient(x-tail,y,x,y);
							gradient.addColorStop("0","black");
							gradient.addColorStop("1.0","grey");

							ctx.beginPath();
					        ctx.moveTo(x, y);

							ctx.moveTo(x-tail, y);
							ctx.fillStyle=gradient;
							ctx.fillRect(x-tail,y,tail,1);
							
							ctx.closePath();
					        ctx.fill();
						}
					}
					setTimeout(function() {
						drawStars();
					}, 15);
				}

				generateStars();
				drawStars();
			});

		</script>
	</head>
	
	<body>
		<canvas id="myCanvas">
		</canvas>
	</body>

</html>