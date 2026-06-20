import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './MainPage.css';
import { EC2_URL, LAMBDA_URL, ECS_URL } from './api';

function MainPage() {
    const navigate = useNavigate();
    const [subscriptions, setSubscriptions] = useState([]);
    const [queryResult, setQueryResult] = useState(null);
    const [formData, setFormData] = useState({ title: '', year: '', artist: '', album: '' });

    const userEmail = sessionStorage.getItem("user_email");
    const userName  = sessionStorage.getItem("user_name") || "User";

    // Logout
    const handleLogout = () => {
        sessionStorage.clear();
        navigate('/');
    };

    // Load subscriptions on mount
    useEffect(() => {
        fetch(`${ECS_URL}/subscriptions/${userEmail}`)
            .then(r => r.json())
            .then(data => {
                if (data.success) setSubscriptions(data.items);
            });
    }, []);

    // Remove subscription
    const handleRemove = async (song) => {
        const key = `${song.artist}#${song.title}#${song.year}`;
        await fetch(`${ECS_URL}/subscriptions/${userEmail}/${encodeURIComponent(key)}`, {
            method: "DELETE"
        });
        setSubscriptions(subscriptions.filter(
            s => !(s.artist === song.artist && s.title === song.title && s.year === song.year)
        ));
    };

    // Query music
    const handleQuery = async (e) => {
    e.preventDefault();
    const { title, year, artist, album } = formData;

    if (!title && !year && !artist && !album) {
        alert("At least one field must be completed.");
        return;
    }

    const params = new URLSearchParams();
    if (title)  params.append("title", title);
    if (year)   params.append("year", year);
    if (artist) params.append("artist", artist);
    if (album)  params.append("album", album);

    try {
        const res = await fetch(`${LAMBDA_URL}/music/query?${params}`);
        const data = await res.json();
        console.log("Query response:", data); // shows response in console
        setQueryResult(data.success ? data.items : []);
    } catch (err) {
        console.error("Query failed:", err);
        alert(`Query failed: ${err.message}`);
    }
};

    // Subscribe
    const handleSubscribe = async (song) => {
        await fetch(`${ECS_URL}/subscriptions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: userEmail, song })
        });
        setSubscriptions([...subscriptions, song]);
    };

    return (
        <div className="main-container">
            <header className="user-area">
                <span>Welcome, <strong>{userName}</strong></span>
                <button onClick={handleLogout} className="logout-link">Logout</button>
            </header>

            <div className="dashboard-grid">
                <section className="subscription-area">
                    <h2>Your Subscriptions</h2>
                    {subscriptions.length === 0 ? (
                        <p className="clean-state">Your subscription area is currently empty.</p>
                    ) : (
                        subscriptions.map(song => (
                            <div key={`${song.artist}-${song.title}-${song.year}`} className="music-card">
                                <img src={song.s3_image_url} alt={song.artist} className="artist-img" />
                                <div className="song-info">
                                    <p>{song.title} ({song.year})</p>
                                    <p>{song.artist} - {song.album}</p>
                                    <button onClick={() => handleRemove(song)}>Remove</button>
                                </div>
                            </div>
                        ))
                    )}
                </section>

                <section className="query-area">
                    <h2>Search Music</h2>
                    <form className="query-form" onSubmit={handleQuery}>
                        <input type="text" placeholder="Title" onChange={(e) => setFormData({...formData, title: e.target.value})} />
                        <input type="text" placeholder="Year" onChange={(e) => setFormData({...formData, year: e.target.value})} />
                        <input type="text" placeholder="Artist" onChange={(e) => setFormData({...formData, artist: e.target.value})} />
                        <input type="text" placeholder="Album" onChange={(e) => setFormData({...formData, album: e.target.value})} />
                        <button type="submit">Query</button>
                    </form>

                    <div className="results-area">
                        {queryResult === null ? null : queryResult.length === 0 ? (
                            <p>No result is retrieved. Please query again.</p>
                        ) : (
                            queryResult.map(song => (
                                <div key={`${song.artist}-${song.title}-${song.year}`} className="music-card">
                                    <img src={song.s3_image_url} alt={song.artist} className="artist-img" />
                                    <div className="song-info">
                                        <p>{song.title} - {song.artist}</p>
                                        <p>{song.album} ({song.year})</p>
                                        <button onClick={() => handleSubscribe(song)}>Subscribe</button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </section>
            </div>
        </div>
    );
}

export default MainPage;