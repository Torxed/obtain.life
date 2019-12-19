<?php
	session_start();
	if (!isset($_SESSION['loggedin'])) {
		header('Location: /login.php');
		exit();
	}
?>
<HTML>
	<head>
		<title>TargetTest - Automated Security Tests</title>
		<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>
		<link rel="stylesheet" href="/uikit/css/uikit.min.css" />
		<link id="data-uikit-theme" rel="stylesheet" href="/uikit/css/uikit.docs.min.css">
		<script src="/uikit/js/uikit.min.js"></script>

		<script src="http://cdn.zingchart.com/zingchart.min.js"></script>
		<style type="text/css">
			body {
				background-color: #070802;
				/* Credit: http://www.vangviet.com/fantastic-wood-floor-wallpapers/ */
				background-image: url('/resources/img/wood.png');
				background-attachment: fixed;
				-webkit-background-size: cover;
				-moz-background-size: cover;
				-o-background-size: cover;
				background-size: cover;
			}
			hr {
				margin: 0px;
				padding: 0px;
			}
			a {
				color: #642887;
			}

			a.critical {
				color: #FF6600;
			}

			.content {
				width: 100%;
			}
			.contentData {
				margin-top: 20px;
				margin-left: 20px;
				margin-right: 20px;
				padding-bottom: 20px;
			}


			.logo {
				background-image: url('/resources/img/logo.png');
				margin: 0px;
				padding-left: 10px;
				height: 42px;
				width: 110px;
				overflow: hidden;
				background-size: 100%;
				background-repeat: no-repeat;
				background-position: 10px 0px;
				background-color: rgba(255,255,255,1);
			}

			.uk-navbar {
				border-radius: 0px !important;
				background: #642887 !important;
			}
			.uk-navbar-nav>li>a {
				color: #e2e2e2 !important;
				text-shadow: 0 1px 0 rgba(120,40,120,0.4) !important;
			}
			.footer {
				font-size: 10px;
				text-align: right;
				margin: 0px;
				padding: 0px;
			}

			/* Theme */
			.uk-panel-box-statistics {
				background-color: #bbc7dd;
				border: 1px solid #bbc7ed;
			}

			.uk-navbar-nav>li.uk-active>a {
				color: #a2a2a2 !important;
			}

			#chartDivContainer {
				height: 380px;
				overflow: hidden;
			}

		</style>

		<script type="text/javascript">
			$(document).ready(function() {
				var graphdata = {
				    "graphset": [
				        {
				            "type": "area",
				            "stacked": true,
				            "background-color": "transparent",
				            "title": {
				                "font-family": "arial",
				                "font-size": "20px",
				                "font-weight": "normal",
				                "background-color": "none",
				                "offset-x": "35%",
				                "offset-y": "20%",
				                "text-align": "left"
				            },
				            "legend": {
				                "margin":"5% auto auto auto",
				                "layout": "float",
				                "font-family": "arial",
				                "font-size": "10px",
				                "background-color": "#1D2629",
				                "border-color": "#808080",
				                "toggle-action": "remove",
				                "item": {
				                    "marker-style": "circle",
				                    "font-color": "#ffffff"
				                }
				            },
				            "plot": {
				                "tooltip-text": "%t: %v",
				                "animation": {
				                    "speed": 0.5,
				                    "effect": 4
				                },
				                "shadow": false
				            },
				            "plotarea": {
				                "margin": "22% 8% 14% 16%"
				            },
				            "series": [
				                {
				                    "text": "Network scans",
				                    "values": [ 
				                        63,
				                        40,
				                        33,
				                        39,
				                        70,
				                        63,
				                        63
				                    ],
				                    "line-width": "2px",
				                    "line-color": "#8DD62E",
				                    "background-color": "#8DD62E",
				                    "marker": {
				                        "type": "circle",
				                        "size": "4px",
				                        "border-width": "0px",
				                        "background-color": "#8DD62E",
				                        "border-color": "#8DD62E",
				                        "shadow": false
				                    }
				                },
				                {
				                    "text": "Device Specific",
				                    "values": [
				                        30,
				                        33,
				                        61,
				                        53,
				                        27,
				                        28,
				                        28
				                    ],
				                    "line-width": "2px",
				                    "line-color": "#FF006F",
				                    "background-color": "#FF006F",
				                    "marker": {
				                        "type": "circle",
				                        "size": "4px",
				                        "border-width": "0px",
				                        "background-color": "#FF006F",
				                        "border-color": "#FF006F",
				                        "shadow": false
				                    }
				                },
				                {
				                    "text": "Social Attacks",
				                    "values": [
				                        8,
				                        5,
				                        5,
				                        1,
				                        4,
				                        6,
				                        6
				                    ],
				                    "line-width": "2px",
				                    "line-color": "#00D3E6",
				                    "background-color": "#00D3E6",
				                    "marker": {
				                        "type": "circle",
				                        "size": "4px",
				                        "border-width": "0px",
				                        "background-color": "#00D3E6",
				                        "border-color": "#00D3E6",
				                        "shadow": false
				                    }
				                },
				                {
				                    "text": "Brute Force",
				                    "values": [
				                        10,
				                        13,
				                        12,
				                        8,
				                        15,
				                        9,
				                        9
				                    ],
				                    "line-width": "2px",
				                    "line-color": "#FFD540",
				                    "background-color": "#FFD540",
				                    "marker": {
				                        "type": "circle",
				                        "size": "4px",
				                        "border-width": "0px",
				                        "background-color": "#FFD540",
				                        "border-color": "#FFD540",
				                        "shadow": false
				                    }
				                }
				            ],
				            "scale-x": {
				                "values": [
				                    "Mon",
				                    "Tue",
				                    "Wed",
				                    "Thu",
				                    "Fri",
				                    "Sat",
				                    "Sun",
				                ],
				                "line-color": "#808080",
				                "line-width": "1px",
				                "line-style": "solid",
				                "guide": {
				                    "line-color": "#808080",
				                    "line-style": "solid"
				                },
				                "tick": {
				                    "line-width": "1px",
				                    "line-color": "#808080"
				                },
				                "item": {
				                    "font-size": "12px",
				                    "font-color": "#808080",
				                    "font-weight": "normal",
				                    "font-family": "arial",
				                    "offset-y": "5%"
				                }
				            },
				            "scale-y": {
				                "values": "0:150:50",
				                "format": "%v targets",
				                "line-width": "1px",
				                "line-color": "#808080",
				                "guide": {
				                    "line-color": "#808080",
				                    "alpha": 0.1,
				                    "line-style": "solid"
				                },
				                "tick": {
				                    "line-width": "1px",
				                    "line-color": "#808080"
				                },
				                "item": {
				                    "font-size": "12px",
				                    "font-color": "#808080",
				                    "font-weight": "normal",
				                    "font-family": "arial",
				                    "offset-x": "-5%"
				                }
				            },
				            "crosshair-x": {
				                "line-width": "2px",
				                "line-color": "#FFFFFF",
				                "offset-y": "10%",
				                "marker": {
				                    "visible": false
				                },
				                "plot-label": {
				                    "text": "<strong>%t</strong>: %v gal",
				                    "font-color": "#000000",
				                    "font-family": "arial"
				                },
				                "scale-label": {
				                    "background-transparent": true,
				                    "offset-y": "5%"
				                }
				            },
				            "tooltip": {
				                "visible": false
				            }
				        }
				    ]
				}

				var graphdata2 = {
					"graphset":[
						{
							"type":"bubble",
							"background-color":"transparent",
							"title":{ "text":"Vulnerability Heat Map", "background-color":"transparent", "font-color":"#642887" },
							"legend":{ "layout":"1x3", "x": "25%", "y": "360px", "border-width":0, "shadow":0,"background-color":"transparent", "alpha":1, "item":{ "color":"red" } },
							"series":[
								{
									"values":[
										[1,15,4],
										[2.4,4.8,2],
										[5,10.2,1],
										[6,7,8.3],
										[3,6,2],
										[7.6,15.1,1],
										[8,2.5,4],
										[1,7,3.8],
										[2.9,12,3],
										[4,4.5,4],
										[5.5,1.9,2],
										[6,3,1],
										[8,16,2]
									],
									"text": "Windows"
								},
								{
									"values":[
										[3.4,5,8.2],
										[2,17,2],
										[8.3,8,3.7],
										[4.4,6.5,2],
										[7.1,3,4],
										[2,12,1.9],
										[1,4,1],
										[6.2,2,6.5],
										[4,10,3],
										[6,14.5,2],
										[2,6,2]
									],
									"text": "Linux/Unix"
								},
								{
									"values":[
										[3.6,11,4.5],
										[6.5,7.4,4.9],
										[8,14,3],
										[3.2,8,3],
										[5,5,2.9],
										[7.5,10.1,2],
										[2,1,6],
										[7,4,1],
										[6,16,2.9],
										[1,8,3],
										[5,14,10]
									],
									"text": "OSX"
								}
							]
						}
					]
				}

				zingchart.render({
					id:'chartDiv',
					height:400,
					width:"100%",
					data: graphdata
				});

				zingchart.render({
					id:'chartDiv2',
					height:400,
					width:"100%",
					data: graphdata2
				});
			});
		</script>
	</head>
<body>
	<nav class="uk-navbar">
		<ul class="uk-navbar-nav">
			<li style="margin: -2px; padding: 0px;">
				<a href="" style="padding: 0px; margin: 0px;">
					<div class="logo">
					</div>
				</a>
			</li>
			<li>
				<a href="" class="uk-navbar-nav-subtitle">
					Dashboard
					<div>News, graphs...</div>
				</a>
			</li>

			<li data-uk-dropdown="{mode:'hover'}" class="uk-active">
				<a href="syshealth.php" class="uk-navbar-nav-subtitle">
					System Health
					<div>Active scans, sys load...</div>
					<div class="uk-dropdown uk-dropdown-small">
						<ul class="uk-nav uk-nav-dropdown">
							<li><a href="">Environmental report</a></li>
						</ul>
					</div>
				</a>
			</li>
			<li>
				<a href="" class="uk-navbar-nav-subtitle">
					Reports & Logs
					<div>System logs, Generate reports</div>
				</a>
			</li>
			<li>
				<a href="">
					Administration
				</a>
			</li>
		</ul>
		<div class="uk-navbar-content uk-navbar-flip  uk-hidden-small">
			<div class="uk-button-group">
				<a class="uk-button uk-button-danger" href="#">Log out</a>
			</div>
		</div>
	</nav>

	<div class="content">
		<div class="contentData">
			<ul class="uk-grid" data-uk-grid-margin>

				<!-- These elements have a width in percent -->
				<li class="uk-width-medium-2-10 uk-push-1-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Status <a href="#" class="critical">Critical</a></div>
						<p>Report engine is not responding.</p>
						<hr><div class="footer">2015-05-30</div>
					</div>
				</li>
				<li class="uk-width-medium-2-10 uk-push-1-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Written by <a href="#">System</a></div>
						<p>A scheduled maintanance is due 2015-06-12.</p>
						<hr><div class="footer">2015-05-27</div>
					</div>
				</li>
				<li class="uk-width-medium-2-10 uk-push-1-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Written by <a href="#">System</a></div>
						<p>A full system backup is scheduled for 2015-05-25.</p>
						<hr><div class="footer">2015-05-13</div>
					</div>
				</li>
				<li class="uk-width-medium-2-10 uk-push-1-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Written by <a href="#">System</a></div>
						<p>A system upgrade is due 2015-05-04</p>
						<hr><div class="footer">2015-04-22</div>
					</div>
				</li>
				<li class="uk-width-medium-10-10 uk-pusj-1-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary">
						<div id="chartDivContainer"><div id='chartDiv'></div></div>
					</div>
				</li>

	 			<li class="uk-width-medium-2-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Status <a href="#" class="critical">Critical</a></div>
						<p>Report engine is not responding.</p>
						<hr><div class="footer">2015-05-30</div>
					</div>
					<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Status <a href="#">Information</a></div>
						<p>Slight latency detected during network scans.</p>
						<hr><div class="footer">2015-05-24</div>
					</div>
				</li>
	<!--				<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
						<div class="headline">Written by <a href="#">System</a></div>
						<p>A scheduled maintanance is due 2015-06-12.</p>
						<hr><div class="footer">2015-05-30</div>
					</div>
				</li>-->
				<li class="uk-width-medium-8-10">
					<div class="uk-panel uk-panel-box uk-panel-box-primary">
						<div id="chartDivContainer"><div id='chartDiv2'></div></div>
					</div>
				</li>

				<!-- Include:
				http://www.zingchart.com/gallery/chart/#!interactive-sales-dashboard
				-->

			</ul>
		</div>
	</div>
</body>
</HTML>