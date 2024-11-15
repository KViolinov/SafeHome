<?php
session_start();

// Firebase configuration
define('FIREBASE_URL', 'https://safehome-c4576-default-rtdb.firebaseio.com/users.json'); // Firebase URL
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

// Auto-login if "remember me" cookie is set
if (!isset($_SESSION['username']) && isset($_COOKIE['user_email'])) {
    $_SESSION['username'] = $_COOKIE['user_email'];
}

// Handle signup
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['signup'])) {
    // Signup code remains the same as your original
}

// Handle login
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['login'])) {
    $email = htmlspecialchars($_POST['email']);
    $password = htmlspecialchars($_POST['password']);
    $remember = isset($_POST['remember']);

    // Sign in user
    $login_url = FIREBASE_AUTH_URL . 'signInWithPassword?key=AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI';
    $login_data = [
        'email' => $email,
        'password' => $password,
        'returnSecureToken' => true
    ];

    $login_response = firebaseRequest($login_url, 'POST', $login_data);
    
    if (isset($login_response['idToken'])) {
        $_SESSION['username'] = $email;

        // Set a cookie if "Remember Me" is checked
        if ($remember) {
            setcookie('user_email', $email, time() + (86400 * 30), "/");
        }
        echo "<script>alert('User logged in successfully!');</script>";
    } else {
        echo 'Error logging in: ' . $login_response['error']['message'];
    }
}

// Handle logout
if (isset($_POST['logout'])) {
    session_unset();
    session_destroy();

    // Delete "Remember Me" cookie on logout
    setcookie('user_email', '', time() - 3600, "/");
    header('Location: profile.php');
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafeHome - Home</title>
    <link rel="stylesheet" href="style.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f4f8;
            color: #333;
            text-align: center; /* Centering all the text */
        }

        header {
            background-color: #34495e;
            padding: 20px;
            color: #fff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            margin: 0;
            font-size: 2.5rem;
        }

        header nav ul {
            list-style: none;
            padding: 0;
            margin: 20px 0 0;
        }

        header nav ul li {
            display: inline;
            margin-right: 30px;
        }

        header nav ul li a {
            color: #fff;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: bold;
            transition: color 0.3s ease;
        }

        header nav ul li a:hover {
            color: #f39c12;
        }

        .container {
            display: flex;
            justify-content: center; /* Center the container */
            gap: 30px;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Highlight the active link */
nav ul li a.active {
    background-color: #2980b9; /* Change the background color to highlight */
    color: white; /* Make text white for better contrast */
    font-weight: bold; /* Optional: Make the active link bold */
}

        h2 {
            font-size: 1.8rem;
            color: #2c3e50;
        }

        .project-info {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            width: 60%; /* Adjusting the width for better centering */
            margin: 0 auto;
            transition: transform 0.3s ease;
        }

        .project-info:hover {
            transform: translateY(-5px);
        }

        .project-info h3 {
            color: #3498db;
            margin-bottom: 10px;
        }

        .project-info ul {
            padding-left: 20px;
            font-size: 1.1rem;
        }

        .project-info ul li {
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .project-info p {
            font-size: 1.1rem;
            line-height: 1.8;
        }

        .user-info {
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>

<body>

    <header>
        <h1>Welcome to SafeHome</h1>
        <nav>
            <ul>
                <li><a href="index.php">Home</a></li>
                <li><a href="dashboard.php">Dashboard</a></li>
                <li><a href="configure.php">Configure Camera</a></li>
                <li><a href="profile.php" class="active">Profile</a></li>
            </ul>
        </nav>

        <?php if ($username): ?>
<div class="user-info">
    <p>Logged in as: <?php echo htmlspecialchars($username); ?></p>
</div>
<?php endif; ?>

    </header>

    <main>
            <h2>User Authentication</h2>

            <?php if (!isset($_SESSION['username'])): ?>
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
                    <div class="form-group">
                        <input type="checkbox" id="remember" name="remember">
                        <label for="remember" class="checkbox-label">Remember Me</label>
                    </div>
                    <button type="submit" name="login">Login</button>
                </form>
            <?php else: ?>
                <h3>User Information</h3>
                <p>Username: <?php echo $_SESSION['username']; ?></p>
                <form action="#" method="POST">
                    <button type="submit" name="logout">Sign Out</button>
                </form>
            <?php endif; ?>
        </main>


</body>
</html>
