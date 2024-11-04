<?php
session_start();
// Firebase configuration
define('FIREBASE_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json'); // Replace with your Firebase URL
define('FIREBASE_USER_DEVICES_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/userDevices.json'); // Firebase user devices URL

// Function to fetch data from Firebase using cURL
function fetchDataFromFirebase() {
    $url = FIREBASE_URL;
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    $json_data = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close($ch);
    return json_decode($json_data, true);
}

// Function to add a device to the user's dashboard
function addToUserDashboard($username, $macAddress) {
    $url = FIREBASE_USER_DEVICES_URL;
    $data = [
        'username' => $username,
        'macAddress' => $macAddress
    ];
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_POST, true);
    curl_exec($ch);
    curl_close($ch);
}

// Fetch device links from Firebase
$device_links = fetchDataFromFirebase();

// Search functionality variables (initialize empty)
$search_mac = "";
$filtered_links = [];

// Check if search form submitted
if (isset($_POST['search_mac'])) {
    $search_mac = htmlspecialchars($_POST['search_mac']);
    foreach ($device_links as $mac => $url) {
        if (stristr($mac, $search_mac) !== false) {
            $filtered_links[$mac] = $url;
        }
    }
}

// Handle "Add to Dashboard" action
if (isset($_POST['add_to_dashboard'])) {
    $macAddress = htmlspecialchars($_POST['mac_address']);
    $username = $_SESSION['username']; // Ensure the user is logged in
    addToUserDashboard($username, $macAddress);
    echo 'Device added to your dashboard successfully!';
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configure Camera</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Profile</h1>
            <nav>
                <ul>
                    <li><a href="index.php">Dashboard</a></li>
                    <li><a href="configure.php">Configure Camera</a></li>
                    <li><a href="profile.php">Profile</a></li>
                </ul>
            </nav>
            <?php if (isset($_SESSION['username'])): ?>
                <div class="user-info">
                    <p>Logged in as: <?php echo $_SESSION['username']; ?></p>
                </div>
            <?php endif; ?>
        </header>

        <main>
            <h2>Discovered Device Links</h2>

            <!-- Search form -->
            <form method="post" class="mb-3 d-flex" style="max-width: 400px; margin-bottom: 20px;">
                <input type="text" name="search_mac" class="form-control" placeholder="Search by MAC Address" style="flex: 1;">
                <button type="submit" class="btn btn-primary ml-2">Search</button>
            </form>

            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>MAC Address</th>
                        <th>Link</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (!empty($filtered_links)): ?>
                        <?php foreach ($filtered_links as $mac => $url): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($mac); ?></td>
                                <td><a href="<?php echo htmlspecialchars($url); ?>" target="_blank"><?php echo htmlspecialchars($url); ?></a></td>
                                <td>
                                    <form method="post" action="#">
                                        <input type="hidden" name="mac_address" value="<?php echo htmlspecialchars($mac); ?>">
                                        <button type="submit" name="add_to_dashboard" class="btn btn-success">Add to Dashboard</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php elseif (isset($_POST['search_mac']) && empty($filtered_links)): ?>
                        <tr>
                            <td colspan="3">No devices found for "<?php echo htmlspecialchars($search_mac); ?>".</td>
                        </tr>
                    <?php else: ?>
                        <tr>
                            <td colspan="3">No devices found.</td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>
