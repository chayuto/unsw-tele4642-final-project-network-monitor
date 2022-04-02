<html>
<body>
Block List: blockList.csv 

<?php
echo "<table border=\"1\">\n\n";
$f = fopen("blockList.csv", "r");
while (($line = fgetcsv($f)) !== false) {
        echo "<tr>";
        foreach ($line as $cell) {
                echo "<td>" . htmlspecialchars($cell) . "</td>";
        }
        echo "</tr>\n";
}
fclose($f);
echo "\n</table> <br>";

?>
<hr>
<p> Future implimentation:policy UI </p>
Block IP 
<form action="UAC_get.php" method="get">
IP: <input type="text" name="ip"><br>
<input type="submit">
</form>

<hr>

Unlock IP (Proj UI extension)
<form action="UAC_get.php" method="get">
IP: <input type="text" name="ip"><br>
<input type="submit">
</form>

</body>
</html>
