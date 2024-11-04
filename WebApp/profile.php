<?php
session_start(); // Start the session

// Firebase configuration
define('FIREBASE_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/users.json'); // Replace with your Firebase URL
define('FIREBASE_AUTH_URL', 'https://identitytoolkit.googleapis.com/v1/accounts:'); // Firebase Auth API

// Function to handle Firebase requests
function firebaseRequest($url, $method = 'GET', $data = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    if ($method == 'POST' || $method == 'PUT') {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    }
    
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Handle signup
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['signup'])) {
    $username = htmlspecialchars($_POST['username']);
    $email = htmlspecialchars($_POST['email']);
    $password = htmlspecialchars($_POST['password']);

    // Create user in Firebase Authentication
    $signup_url = FIREBASE_AUTH_URL . 'signUp?key=AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI'; // Replace YOUR_API_KEY with your Firebase API key
    $signup_data = [
        'email' => $email,
        'password' => $password,
        'returnSecureToken' => true
    ];

    $signup_response = firebaseRequest($signup_url, 'POST', $signup_data);
    
    if (isset($signup_response['idToken'])) {
        // Save user information in Firebase Database
        $user_data = [
            'username' => $username,
            'email' => $email
        ];
        $user_url = FIREBASE_URL; // Users endpoint
        firebaseRequest($user_url, 'POST', $user_data);
        
        $_SESSION['username'] = $username; // Store username in session
        echo 'User signed up successfully!';
    } else {
        echo 'Error signing up: ' . $signup_response['error']['message'];
    }
}

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $email = htmlspecialchars($_POST['email']);
    $password = htmlspecialchars($_POST['password']);

    // Sign in user
    $login_url = FIREBASE_AUTH_URL . 'signInWithPassword?key=AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI'; // Replace YOUR_API_KEY with your Firebase API key
    $login_data = [
        'email' => $email,
        'password' => $password,
        'returnSecureToken' => true
    ];

    $login_response = firebaseRequest($login_url, 'POST', $login_data);
    
    if (isset($login_response['idToken'])) {
        // Retrieve username from Firebase Database (you may store it during signup or fetch it)
        $_SESSION['username'] = $login_response['email']; // Store email in session for now
        echo 'User logged in successfully!';
    } else {
        echo 'Error logging in: ' . $login_response['error']['message'];
    }
}

// Handle logout
if (isset($_POST['logout'])) {
    session_unset(); // Clear the session
    session_destroy(); // Destroy the session
    header('Location: profile.php'); // Redirect to profile page
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile</title>
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
            <h2>User Authentication</h2>

            <?php if (!isset($_SESSION['username'])): // Show signup and login forms if not logged in ?>
                <h3>Sign Up</h3>
                <form action="#" method="POST">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" name="signup">Sign Up</button>
                </form>

                <h3>Login</h3>
                <form action="#" method="POST">
                    <div class="form-group">
                        <label for="login-email">Email:</label>
                        <input type="email" id="login-email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="login-password">Password:</label>
                        <input type="password" id="login-password" name="password" required>
                    </div>
                    <button type="submit" name="login">Login</button>
                </form>
            <?php else: // User is logged in ?>
                <h3>User Information</h3>
                <p>Username: <?php echo $_SESSION['username']; ?></p>
                <form action="#" method="POST">
                    <button type="submit" name="logout">Sign Out</button>
                </form>
            <?php endif; ?>
        </main>
    </div>
</body>
</html>
