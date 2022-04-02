<!DOCTYPE html>

<html lang="en-US">

<head>
	<meta http-equiv="refresh" content="10">	
	<title>TELE4642 Project!</title>
</head> 
<body>

Detailed User Stat<br><br>

<?php
$dirname = "userReport/";
$images = glob($dirname."*.png");
foreach($images as $image) {
echo '<img src="'.$image.'"" alt="Test plot" style="width:304px;height:228px"  /><br />';
}
?>


<hr>
<a href="http://tele.chayut.me">Back to main page</a><br>
<br>

</body>
</html>



