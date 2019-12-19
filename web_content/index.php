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
			}
			hr {
				margin: 0px;
				padding: 0px;
			}
			a {
				color: #642887;
			}

			.content {
				padding: 20px;
				width: 100%;
				height: 100%;
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

			#chartDivContainer {
				height: 380px;
				overflow: hidden;
			}

		</style>

		<script type="text/javascript">
			$(document).ready(function() {
				var graphdata = {
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

			<li data-uk-dropdown="{mode:'hover'}">
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
		<ul class="uk-grid" data-uk-grid-margin>

			<!-- These elements have a width in percent -->
			<li class="uk-width-medium-2-10">
				<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
					<div class="headline">Written by <a href="#">System</a></div>
					<p>A new weekly technical report has been automatically generated.
					<hr><div class="footer">2015-05-30</div>
				</div>
				<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
					<div class="headline">Written by <a href="#">System</a></div>
					<p>A new weekly technical report has been automatically generated.
					<hr><div class="footer">2015-05-30</div>
				</div>
				<div class="uk-panel uk-panel-box uk-panel-box-primary" style="padding-bottom: 0px;">
					<div class="headline">Written by <a href="#">System</a></div>
					<p>A new weekly technical report has been automatically generated.
					<hr><div class="footer">2015-05-30</div>
				</div>
			</li>
			<li class="uk-width-medium-7-10">
				<div class="uk-panel uk-panel-box uk-panel-box-primary">
					<div id="chartDivContainer"><div id='chartDiv'></div></div>
				</div>
			</li>
			<li class="uk-width-medium-3-5">
				<div class="uk-panel uk-panel-box uk-panel-box-primary">
					World news
				</div>
			</li>
			<li class="uk-width-medium-3-10">
				<div class="uk-panel uk-panel-box uk-panel-box-primary">
					Quick overview of how the system is feeling, no details tho because that comes later. This will just show like actual alerts, some warnings etc.
					<dl class="uk-description-list-horizontal uk-description-list-line">
						<dt>Found hosts</dt>
						<dd>1376</dd>

						<dt>Scanned hosts</dt>
						<dd>346</dd>

						<dt>Found hosts</dt>
						<dd>376</dd>
					</dl>
				</div>
			</li>

		</ul>
	</div>
</body>
</HTML>