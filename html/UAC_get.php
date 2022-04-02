<html>
<body>

(test) Blocking IP: 
<?php 
	$IP = $_GET["ip"];
	echo $IP ; 
	$f = fopen("blockList.csv", "a");
	fwrite($f,$IP. "\n");
	fclose($f);

?>
<br>




<a href = "http://tele.chayut.me">Main Page</a>
</body>
</html>
