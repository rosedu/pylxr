<?
        $config = $_GET['config'];
        $search = $_GET['search'];
        $handle = popen("python dbaccess/xapianSearch.py ".$config." ".$search, "r");
        $read = fgets($handle);
        echo $read;
        pclose($handle);
?>
