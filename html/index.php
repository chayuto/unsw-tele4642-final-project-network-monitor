<!DOCTYPE html>

<html lang="en-US">

<head>
<meta http-equiv="refresh" content="10">	
	<title>TELE4642 Project!</title>
</head> 
<body>

<center><h1>TELE4642 Network Supervisor</h1>
<p>Authors: Chayut O., Thanchanok S., Vincent F., Michael S.</p>
<p> Tag: Software Defined Network, SDN, Mininet, POX, Statistic, Python, PHP </p>
</center>
<hr>
<p>4642 LAMPS Stack </p>
L(inux)
A(pache)
M(ininet)
P(ox + Python + PHP)
S(Oftware Defined Network)
<hr>


<h2>Network Reports</h2>

<img src="plotHost.png" alt="Test plot" style="width:400px;height:300px">
<img src="plotServ.png" alt="Test plot" style="width:400px;height:300px"><br>

<br>
<a href="/userStat.php">1. Detailed Statistic by User Device</a> <br>
<a href="/servReport.php">2. Detailed Statistic by Application</a> <br>

<hr>
<p>Network Control Panel </p>
<a href="/policy.php">3. Monitoring Policy Control</a><br>
<a href="/UAC.php">4. User Access Control</a>
<hr>


<h2> Stat Tables </h2>
Hosts <br>

<?php

echo "<table border=\"1\">\n\n";
$f = fopen("hostName.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);

echo "\n</table> <br> App list <br>";

echo "<table border=\"1\">\n\n";
$f = fopen("servName.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table>";


?> <br>

Total Usage This Month (Bytes) <br>
<?php
echo "<table border=\"1\">\n\n";
$f = fopen("totalUsage.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table>";
?>

<br>

User Activities in past hour (Bytes) <br>
<?php
echo "<table border=\"1\">\n\n";
$f = fopen("testTable.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table>";
?>
<hr>

<a href="/flowStat/">FlowStat History</a>
<a href="/externalFlow/">Ext FlowStat History</a>
<a href="/internalFlow/">Int FlowStat History</a>
<hr>

Wiki: <a href="http://tele4642group4.wikispaces.com">http://tele4642group4.wikispaces.com</a><br>
 <a href="http://wiki.tele.chayut.me">wiki.tele.chayut.me</a>

<hr>
<p>Source Code</p>
<a href="/underConstruction.html">Code</a> <br>

<hr>

</body>
</html>

