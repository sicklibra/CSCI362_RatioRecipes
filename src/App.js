// Import the app's CSS styles
import './App.css';
// Import React's useState hook for managing state
import { useState, useEffect } from 'react';
// Import Firestore functions for adding documents
import { collection, addDoc } from 'firebase/firestore';
// Import the Firestore instance and projectId from firebase.js
import { firestore, auth, projectId } from './firebase';
// Import the Firebase Auth functions we'll use for email/password auth
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from 'firebase/auth';
function App() {
  // State variable to hold the user's input value for Firestore
  const [inputValue, setInputValue] = useState("");
  // State variable to hold the user's name for Firestore
  const [userName, setUserName] = useState("");
  // State variable to hold status messages (success or error)
  const [status, setStatus] = useState("");
  // Authentication state: email and password fields for signup/login
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  // Holds the currently signed-in user (null when signed-out)
  const [currentUser, setCurrentUser] = useState(null);

  // Recipe form state
  const [recipeName, setRecipeName] = useState("");
  const [recipeDescription, setRecipeDescription] = useState("");
  const [unit, setUnit] = useState('g');
  const [totalWeight, setTotalWeight] = useState('');
  const [ingredientsText, setIngredientsText] = useState('[{"name":"flour","weight":200},{"name":"water","weight":120}]');
  const [scaleFactor, setScaleFactor] = useState('1');

  // Function to update inputValue as the user types in the value field
  const handleInputChange = (e) => {
    setInputValue(e.target.value); // Set inputValue to the current value of the input field
  };

  // Save + scale recipe by calling the HTTPS Cloud Function
  const handleSaveRecipe = async () => {
    setStatus('Saving recipe...');
    try {
      const ingredients = JSON.parse(ingredientsText);
      const payload = {
        name: recipeName,
        description: recipeDescription,
        ingredients: ingredients,
        unit: unit,
        totwt: totalWeight ? parseFloat(totalWeight) : 0,
        scale: scaleFactor ? parseFloat(scaleFactor) : 1
      };

      // Use deployed function URL. Change region if your function uses a different one.
      const functionUrl = `https://us-central1-${projectId}.cloudfunctions.net/save_and_scale_recipe`;

      const res = await fetch(functionUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || JSON.stringify(data));
      setStatus(`Recipe saved (id: ${data.id})`);
      // clear form
      setRecipeName('');
      setRecipeDescription('');
      setUnit('g');
      setTotalWeight('');
      setIngredientsText('[{"name":"flour","weight":200},{"name":"water","weight":120}]');
      setScaleFactor('1');
    } catch (err) {
      setStatus('Error saving recipe: ' + err.message);
    }
  };

  // Function to update userName as the user types in the name field
  const handleNameChange = (e) => {
    setUserName(e.target.value); // Set userName to the current value of the name field
  };

  // Function to save both inputValue and userName to Firestore when the button is clicked
  const handleSubmit = async () => {
    // Log the user inputs to the console for debugging
    console.log('Submitting to Firestore:', { value: inputValue, name: userName });
    try {
      // Add a new document to the 'recipeType' collection with both attributes: value and name
      await addDoc(collection(firestore, "recipeType"), { value: inputValue, name: userName });
      setStatus("Value and name saved to Firestore!"); // Set status to success message
      setInputValue(""); // Clear the value input field
      setUserName(""); // Clear the name input field
    } catch (error) {
      setStatus("Error saving value: " + error.message); // Set status to error message
    }
  };

  // -------------------- Authentication handlers --------------------
  // Handle creating a new user with email and password
  const handleSignup = async () => {
    try {
      // Create a new Firebase Auth user using the email and password entered
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      // userCredential.user contains the newly created user's info
      setStatus(`Signed up as ${userCredential.user.email}`);
      setEmail(""); // Clear the email input
      setPassword(""); // Clear the password input
    } catch (error) {
      // Show any error returned by Firebase (weak password, malformed email, etc.)
      setStatus('Signup error: ' + error.message);
    }
  };

  // Handle signing in an existing user with email and password
  const handleLogin = async () => {
    try {
      // Sign in using Firebase Auth; if successful, Firebase will return a userCredential
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      setStatus(`Signed in as ${userCredential.user.email}`);
      setEmail("");
      setPassword("");
    } catch (error) {
      setStatus('Login error: ' + error.message);
    }
  };

  // Handle signing out the current user
  const handleSignOut = async () => {
    try {
      await signOut(auth);
      setStatus('Signed out');
    } catch (error) {
      setStatus('Sign out error: ' + error.message);
    }
  };

  // Subscribe to auth state changes when the component mounts so we can show
  // the current user's state in the UI. onAuthStateChanged fires whenever the
  // user signs in or out (and immediately with the current state).
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
    });
    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  // Render the UI: input fields, button, and status message
  return (
    <div className="App"> {/* Main app container */}
      <header className="App-header"> {/* App header section */}
        {/* Input field for user to enter a value to store in Firestore */}
        <input
          type="text" // Input type is text
          value={inputValue} // Value of the input field is inputValue state
          onChange={handleInputChange} // Update inputValue when user types
          placeholder="Enter a value to store" // Placeholder text
        />
        {/* Input field for user to enter their name to store in Firestore */}
        <input
          type="text" // Input type is text
          value={userName} // Value of the input field is userName state
          onChange={handleNameChange} // Update userName when user types
          placeholder="Enter your name" // Placeholder text
          style={{ marginTop: '10px' }} // Add some space above this input
        />
        {/* ---------------- Authentication UI ---------------- */}
        {/* Email input for signup/login */}
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          style={{ marginTop: '16px' }}
        />
        {/* Password input for signup/login */}
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          style={{ marginTop: '8px' }}
        />
        {/* Buttons to create an account or sign in using email/password */}
        <div style={{ marginTop: '8px' }}>
          {/* Create a new account with the entered email/password */}
          <button onClick={handleSignup}>Sign up</button>
          {/* Sign in with an existing account */}
          <button onClick={handleLogin} style={{ marginLeft: '8px' }}>Log in</button>
        </div>
        {/* Show sign-out button only when a user is signed in */}
        {currentUser ? (
          <div style={{ marginTop: '12px' }}>
            {/* Display the signed-in user's email */}
            <p>Signed in as: {currentUser.email}</p>
            {/* Button to sign the user out */}
            <button onClick={handleSignOut}>Sign out</button>
          </div>
        ) : (
          <p style={{ marginTop: '8px' }}>Not signed in</p>
        )}
        {/* Button to save both value and name to Firestore */}
        <button onClick={handleSubmit} style={{ marginTop: '10px' }}>Save to Firestore</button>
        {/* Recipe form: name, description, total weight, ingredients JSON and scale factor */}
        <div style={{ marginTop: '20px', textAlign: 'left', maxWidth: '520px' }}>
          <h3>Save & Scale Recipe</h3>
          <input
            type="text"
            value={recipeName}
            onChange={(e) => setRecipeName(e.target.value)}
            placeholder="Recipe name"
            style={{ width: '100%', marginTop: '6px' }}
          />
          <input
            type="text"
            value={recipeDescription}
            onChange={(e) => setRecipeDescription(e.target.value)}
            placeholder="Short description"
            style={{ width: '100%', marginTop: '6px' }}
          />
          <input
            type="text"
            value={totalWeight}
            onChange={(e) => setTotalWeight(e.target.value)}
            placeholder="Total weight (optional, numeric)"
            style={{ width: '48%', marginTop: '6px', marginRight: '4%' }}
          />
          <input
            type="text"
            value={scaleFactor}
            onChange={(e) => setScaleFactor(e.target.value)}
            placeholder="Scale factor (e.g. 1.5)"
            style={{ width: '48%', marginTop: '6px' }}
          />
          <textarea
            value={ingredientsText}
            onChange={(e) => setIngredientsText(e.target.value)}
            placeholder='Ingredients as JSON e.g. [{"name":"flour","weight":200}]'
            rows={6}
            style={{ width: '100%', marginTop: '8px' }}
          />
          <div style={{ marginTop: '8px' }}>
            <button onClick={handleSaveRecipe}>Save & Scale Recipe</button>
          </div>
        </div>
        {/* Show status message if available (success or error) */}
        {status && <p>{status}</p>}
      </header>
    </div>
  );
}

// Export the App component as the default export
export default App;
