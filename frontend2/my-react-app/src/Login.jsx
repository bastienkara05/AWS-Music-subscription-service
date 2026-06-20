import { useState } from 'react';
import './Login.css';
import { useNavigate } from 'react-router-dom';
import { EC2_URL } from './api';
function Login(){
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [isLogin, setIsLogin] = useState(true);
    const [errorMessage, setErrorMessage] = useState("");

    //for testing error message
const existingUsers = [" ", "admin@rmit.edu.au", "clean@brand.com"];


  

const handleAction = async (e) => {
    e.preventDefault();
    

    if (isLogin) {
        const res = await fetch(`${EC2_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (data.success) {
            sessionStorage.setItem("user_email", data.user.email);
            sessionStorage.setItem("user_name", data.user.user_name);
            navigate('/main');
        } else {
            setErrorMessage(data.message);
        }

    } else {
        const res = await fetch(`${EC2_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, username, password })
        });
        const data = await res.json();

        if (data.success) {
            sessionStorage.setItem("user_email", email);
            sessionStorage.setItem("user_name", username);
            navigate('/main');
        } else {
            setErrorMessage(data.message);
        }
    }
};
  


    return(

        
        <>
        {/*login/registration area*/}
        <div className = "login-container">
            <div className= "login-box">
            <form onSubmit={handleAction}>
                <h1 className ="login-header">{isLogin ? "Welcome Back!" : "Create Account"}</h1>
                <h2 className= "login-header2">Please enter your details</h2>
                {/*text fields*/}
                    <div className = "text-field">
                    <input 
                    type ="email"
                    placeholder = "Email Adress"
                    value ={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required className = "inner-input"/>
                    </div>
                
                {!isLogin && (
                    <div className = "text-field">
                    <input type = "text"
                    placeholder ="username"
                    required className = "inner-input"
                    onChange={(e) => setUsername(e.target.value)}/>
                    
                    </div>
                )}
            
            
                
                    <div className = "text-field">
                    <input type ="password"
                    placeholder = "Password"
                    value ={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required className = "inner-input"/>
                    </div>

                    {/*Error messgae */}
                    {errorMessage && (
                        <div className="error-message">
                            {errorMessage}
                            </div>
                        )}
                
                {/*registration/login hyperlinks*/}
                <button type="submit"
                className = "login-button"
                >{isLogin ? "Login" : "Create Account"}</button>

                <p className="switch-text">
                    {isLogin ? "Dont have an account?" : "Already have an account?"} 
                    <span 
                     onClick={() => {
                         setIsLogin(!isLogin); 
                          setErrorMessage("");  
                          }} 
                          className="toggle-link"
                          >
                      {isLogin ? " Signup" : " Sign in"}
                    </span>
                    </p>
                
            </form>
            </div>
        </div>
        
        
        
        </>


    )
    
}



export default Login;