import React, { useState } from 'react';

export default function CreateTweetForm({ addTweet }) {
    const [username, setUsername] = useState('');
    const [text, setText] = useState('');

    const handleSubmit = (e) => {
    e.preventDefault();
    const u = username.trim();
    const t = text.trim();
    if (!u || !t) return;           // simple validation
    addTweet(u, t);
    setUsername('');
    setText('');
    };

    return (
    <form onSubmit={handleSubmit} style={{ marginTop: 16 }}>
        <div>
        <label>
            Username:{' '}
            <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="your handle"
            required
            />
        </label>
        </div>
        <div style={{ marginTop: 8 }}>
        <label>
            Tweet:{' '}
            <input
            type="text"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="What's happening?"
            required
            />
        </label>
        </div>
        <button type="submit" style={{ marginTop: 8 }}>
        Post Tweet
        </button>
    </form>
    );
}