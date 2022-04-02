<html>
<body>
<center><h1>Manage Monitoring Site</h1></center>
<hr>
<p>Monitoring List: servList.csv</p>

<?php
echo "<table border=\"1\">\n\n";
$f = fopen("servList.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table> <br>";


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

?>


<br>
<hr>
<h2>Future Implemtation: web based policy control </h2>
<p>Add IP</p>
<form action="UAC_get.php" method="get">
IP: <input type="text" name="ip"><br>
<input type="submit">
</form>


<hr>

<p>Remove IP</p>
<form action="UAC_get.php" method="get">
IP: <input type="text" name="ip"><br>
<input type="submit">
</form>


</body>
</html>
