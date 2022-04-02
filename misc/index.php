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
<p>4642 LAMP Stack </p>
L(inux)
A(pache)
M(ininet)
P(ython + PHP)
<hr>


<p>Network Reports</p>

<img src="plotServ.png" alt="Test plot" style="width:304px;height:228px"><br>
<img src="plotHost.png" alt="Test plot" style="width:304px;height:228px">

<br>
<a href="/userStat.php">1. Detailed Statistic by User</a> <br>
<a href="/servReport.php">2. Detailed Statistic by Site</a> <br>

<hr>
<p>Network Control Panel </p>
<a href="/policy.php">3. Monitoring Policy Control</a><br>
<a href="/UAC.php">4. User Access Control(Project extension)</a>
<hr>


<h2> Stat Tables </h2>

<br><br>Total Usage <br>
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

<br><br>User Activities in past minute <br>
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

Wiki:


<hr>
<p>Source Code</p>
<a href="/underConstruction.html">project_switch.py</a> <br>

<hr>

</body>
</html>

