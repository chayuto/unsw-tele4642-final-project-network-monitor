<!DOCTYPE html>

<html lang="en-US">

<head>
	<meta http-equiv="refresh" content="10">	
	<title>TELE4642 Project!</title>
</head> 
<body>

Report by Server<br><br>

<?php
$dirname = "servReport/";
$images = glob($dirname."*.png");
foreach($images as $image) {
echo '<img src="'.$image.'"" alt="Test plot" style="width:400px;height:300px"  /><br />';
}
?>


<hr>
<a href="http://tele.chayut.me">Back to main page</a><br>
<br>

</body>
</html>



