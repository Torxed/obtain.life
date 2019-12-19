<?php
	if (isset($_POST['username']) && isset($_POST['password'])) {
		session_start();
		$u = $_POST['username'];
		$p = $_POST['password'];
		if($u == 'demo' && $p == 'demo') {
			$_SESSION['loggedin'] = $u;
			header('Location: /');
			exit();
		}
	}
?>
<!DOCTYPE html>
<html lang="en">
	<head>
		<title>TargetTest - Automated Security Tests</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, user-scalable=yes, minimum-scale=0.2, maximum-scale=1.0">
		<style>
			body {
				color: #fff;
				font-family:Monospace;
				font-size:13px;
				text-align:center;
				font-weight: bold;

				background-color: #000;
				margin: 0px;
				overflow: hidden;
			}

			.header {
				position: absolute;
				left: 0px;
				top: 0px;
				width: 100%;
				background-color: #282828;
				border-bottom: 1px solid #222222;
				padding: 5px;
				border-top-left-radius: 10px;
				border-top-right-radius: 10px;
			}

			#Login {
				position: absolute;
				top: 150px;
				left: 50%;
				width: 300px;
				margin-left: -150px;
				padding: 5px;
				color: #fff;
				border: 1px solid #272727;
				border-radius: 10px;

				background-color: rgba(120, 120, 120, 0.2);
				overflow: hidden;
			}

			 .inputField {
			 	margin: 5px;
			 	border: 1px solid #272727;
			 	border-radius: 4px;
			 	padding: 5px;
			 	width: 220px;
			 }

			 .button {
			 	width: 90px;
			 	margin-left: 150px;
			 }

			a {
				color: red;
			}
		</style>
	</head>
	<body>

		<div id="container"></div>
		<div id="Login">
			<div class="header">Login to TargetTest</div>
			<br>
			<br>
			<form method="POST" action="">
				<input class="inputField" type="text" name="username"><br>
				<input class="inputField" type="password" name="password"><br>
				<input class="inputField button" type="submit" value="Login">
			</form>
		</div>

		<script src="three.min.js"></script>

		<script src="js/loaders/BinaryLoader.js"></script>

		<script src="js/shaders/ConvolutionShader.js"></script>
		<script src="js/shaders/CopyShader.js"></script>
		<script src="js/shaders/FilmShader.js"></script>
		<script src="js/shaders/FocusShader.js"></script>

		<script src="js/postprocessing/EffectComposer.js"></script>
		<script src="js/postprocessing/MaskPass.js"></script>
		<script src="js/postprocessing/RenderPass.js"></script>
		<script src="js/postprocessing/BloomPass.js"></script>
		<script src="js/postprocessing/ShaderPass.js"></script>
		<script src="js/postprocessing/FilmPass.js"></script>

		<script src="js/Detector.js"></script>

		<script>

			if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

			var SCREEN_HEIGHT = window.innerHeight;
			var SCREEN_WIDTH = window.innerWidth;

			var container;

			var camera, scene, renderer, mesh, directionalLight;

			var parent, meshes = [], clonemeshes = [];

			var p;

			var aloader, bloader;

			var composer, effectFocus;

			var clock = new THREE.Clock();

			init();
			animate();

			function init() {

				container = document.getElementById( 'container' );

				camera = new THREE.PerspectiveCamera( 20, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 50000 );
				camera.position.set( 0, 700, 7000 );

				scene = new THREE.Scene();
				scene.fog = new THREE.FogExp2( 0x000104, 0.0000675 );

				camera.lookAt( scene.position );

				//

				aloader = new THREE.JSONLoader( );
				bloader = new THREE.BinaryLoader( true );

				document.body.appendChild( bloader.statusDomElement );

				/*aloader.load( "obj/terrain.js", function( geometry ) {

					createMesh( geometry, scene, 16.8, -11000, -200,  -5000, 0x00ff44, false );
					createMesh( geometry, scene, 16.8,  11000, -200, -15000, 0x00ff33, false );
					createMesh( geometry, scene, 16.8,      0, -200, -15000, 0x00ff33, false );
					createMesh( geometry, scene, 16.8,      0, -200,  15000, 0x00ff33, false );
					createMesh( geometry, scene, 16.8,  11000, -200,  15000, 0x00ff22, false );
					createMesh( geometry, scene, 16.8, -11000, -200,   5000, 0x00ff11, false );
					createMesh( geometry, scene, 16.8,  13000, -200,   5000, 0x00ff55, false );
					createMesh( geometry, scene, 16.8,  13000, -200,  -5000, 0x00ff66, false );

				} );*/


				bloader.load( "obj/female02/Female02_bin.js", function( geometry ) {

					createMesh( geometry, scene, 4.05, -1000, -350,    0, 0xffdd44, true );
					createMesh( geometry, scene, 4.05,     0, -350,    0, 0xffffff, true );
					createMesh( geometry, scene, 4.05,  1000, -350,  400, 0xff4422, true );
					createMesh( geometry, scene, 4.05,   250, -350, 1500, 0xff9955, true );
					createMesh( geometry, scene, 4.05,   250, -350, 2500, 0xff77dd, true );

				} );

				bloader.load( "obj/male02/Male02_bin.js", function( geometry ) {

					createMesh( geometry, scene, 4.05,  -500, -350,   600, 0xff7744, true );
					createMesh( geometry, scene, 4.05,   500, -350,     0, 0xff5522, true );
					createMesh( geometry, scene, 4.05,  -250, -350,  1500, 0xff9922, true );
					createMesh( geometry, scene, 4.05,  -250, -350, -1500, 0xff99ff, true );

				} );

				//

				renderer = new THREE.WebGLRenderer( { antialias: false } );
				renderer.setClearColor( scene.fog.color );
				renderer.setPixelRatio( window.devicePixelRatio );
				renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
				renderer.autoClear = false;
				renderer.sortObjects = false;
				container.appendChild( renderer.domElement );

				//

				parent = new THREE.Object3D();
				scene.add( parent );

				var grid = new THREE.PointCloud( new THREE.PlaneBufferGeometry( 7000, 17000, 128, 128 ), new THREE.PointCloudMaterial( { color: 0x272727, size: 10 } ) );
				grid.position.y = -400;
				grid.rotation.x = - Math.PI / 2;
				parent.add( grid );

				// postprocessing

				var renderModel = new THREE.RenderPass( scene, camera );
				var effectBloom = new THREE.BloomPass( 0.75 );
				var effectFilm = new THREE.FilmPass( 0.5, 0.5, 1448, false );

				effectFocus = new THREE.ShaderPass( THREE.FocusShader );

				effectFocus.uniforms[ "screenWidth" ].value = window.innerWidth;
				effectFocus.uniforms[ "screenHeight" ].value = window.innerHeight;

				effectFocus.renderToScreen = true;

				composer = new THREE.EffectComposer( renderer );

				composer.addPass( renderModel );
				composer.addPass( effectBloom );
				composer.addPass( effectFilm );
				composer.addPass( effectFocus );

				//

				window.addEventListener( 'resize', onWindowResize, false );

			}

			//

			function onWindowResize( event ) {

				renderer.setSize( window.innerWidth, window.innerHeight );

				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();

				camera.lookAt( scene.position );

				composer.reset();

				effectFocus.uniforms[ "screenWidth" ].value = window.innerWidth;
				effectFocus.uniforms[ "screenHeight" ].value = window.innerHeight;

			}

			//

			function createMesh( originalGeometry, scene, scale, x, y, z, color, dynamic ) {

				var i, c;

				var vertices = originalGeometry.vertices;
				var vl = vertices.length;

				var geometry = new THREE.Geometry();
				var vertices_tmp = [];

				for ( i = 0; i < vl; i ++ ) {

					p = vertices[ i ];

					geometry.vertices[ i ] = p.clone();
					vertices_tmp[ i ] = [ p.x, p.y, p.z, 0, 0 ];

				}

				var clones = [

					[  6000, 0, -4000 ],
					[  5000, 0, 0 ],
					[  1000, 0, 5000 ],
					[  1000, 0, -5000 ],
					[  4000, 0, 2000 ],
					[ -4000, 0, 1000 ],
					[ -5000, 0, -5000 ],

					[ 0, 0, 0 ]

				];

				if ( dynamic ) {

					for ( i = 0; i < clones.length; i ++ ) {

						c = ( i < clones.length -1 ) ? 0x252525 : color;

						mesh = new THREE.PointCloud( geometry, new THREE.PointCloudMaterial( { size: 3, color: c } ) );
						mesh.scale.x = mesh.scale.y = mesh.scale.z = scale;

						mesh.position.x = x + clones[ i ][ 0 ];
						mesh.position.y = y + clones[ i ][ 1 ];
						mesh.position.z = z + clones[ i ][ 2 ];

						parent.add( mesh );

						clonemeshes.push( { mesh: mesh, speed: 0.5 + Math.random() } );

					}

				} else {

					mesh = new THREE.PointCloud( geometry, new THREE.PointCloudMaterial( { size: 3, color: color } ) );
					mesh.scale.x = mesh.scale.y = mesh.scale.z = scale;

					mesh.position.x = x;
					mesh.position.y = y;
					mesh.position.z = z;

					parent.add( mesh );

				}

				bloader.statusDomElement.style.display = "none";

				meshes.push( {
					mesh: mesh, vertices: geometry.vertices, vertices_tmp: vertices_tmp, vl: vl,
					down: 0, up: 0, direction: 0, speed: 35, delay: Math.floor( 200 + 200 * Math.random() ),
					started: false, start: Math.floor( 100 + 200 * Math.random() ),
					dynamic: dynamic
				} );

			}


			var j, jl, cm, data, vertices, vertices_tmp, vl, d, vt;

			function animate () {

				requestAnimationFrame( animate );
				render();

			}

			function render () {

				delta = 10 * clock.getDelta();

				delta = delta < 2 ? delta : 2;

				parent.rotation.y += -0.002 * delta;

				for( j = 0, jl = clonemeshes.length; j < jl; j ++ ) {

					cm = clonemeshes[ j ];
					cm.mesh.rotation.y += -0.01 * delta * cm.speed;

				}

				for( j = 0, jl = meshes.length; j < jl; j ++ ) {

					data = meshes[ j ];
					mesh = data.mesh;
					vertices = data.vertices;
					vertices_tmp = data.vertices_tmp;
					vl = data.vl;

					if ( ! data.dynamic ) continue;

					if ( data.start > 0 ) {

						data.start -= 1;

					} else {

						if ( !data.started ) {

							data.direction = -1;
							data.started = true;

						}

					}

					for ( i = 0; i < vl; i ++ ) {

						p = vertices[ i ];
						vt = vertices_tmp[ i ];

						// falling down

						if ( data.direction < 0 ) {

							// var d = Math.abs( p.x - vertices_tmp[ i ][ 0 ] ) + Math.abs( p.y - vertices_tmp[ i ][ 1 ] ) + Math.abs( p.z - vertices_tmp[ i ][ 2 ] );
							// if ( d < 200 ) {

							if ( p.y > 0 ) {

								// p.y += data.direction * data.speed * delta;

								p.x += 1.5 * ( 0.50 - Math.random() ) * data.speed * delta;
								p.y += 3.0 * ( 0.25 - Math.random() ) * data.speed * delta;
								p.z += 1.5 * ( 0.50 - Math.random() ) * data.speed * delta;

							} else {

								if ( ! vt[ 3 ] ) {

									vt[ 3 ] = 1;
									data.down += 1;

								}

							}

						}

						// rising up

						if ( data.direction > 0 ) {

							//if ( p.y < vertices_tmp[ i ][ 1 ] ) {

							//	p.y += data.direction * data.speed * delta;

							d = Math.abs( p.x - vt[ 0 ] ) + Math.abs( p.y - vt[ 1 ] ) + Math.abs( p.z - vt[ 2 ] );

							if ( d > 1 ) {

								p.x += - ( p.x - vt[ 0 ] ) / d * data.speed * delta * ( 0.85 - Math.random() );
								p.y += - ( p.y - vt[ 1 ] ) / d * data.speed * delta * ( 1 + Math.random() );
								p.z += - ( p.z - vt[ 2 ] ) / d * data.speed * delta * ( 0.85 - Math.random() );

							} else {

								if ( ! vt[ 4 ] ) {

									vt[ 4 ] = 1;
									data.up += 1;

								}

							}

						}


					}

					// all down

					if ( data.down === vl ) {

						if ( data.delay === 0 ) {

							data.direction = 1;
							data.speed = 10;
							data.down = 0;
							data.delay = 320;

							for ( i = 0; i < vl; i ++ ) {

								vertices_tmp[ i ][ 3 ] = 0;

							}

						} else {

							data.delay -= 1;

						}


					}

					// all up

					if ( data.up === vl ) {

						if ( data.delay === 0 ) {

							data.direction = -1;
							data.speed = 35;
							data.up = 0;
							data.delay = 120;

							for ( i = 0; i < vl; i ++ ) {

								vertices_tmp[ i ][ 4 ] = 0;

							}

						} else {

							data.delay -= 1;

						}


					}

					mesh.geometry.verticesNeedUpdate = true;

				}

				renderer.clear();
				composer.render( 0.01 );

			}

		</script>

	</body>

</html>