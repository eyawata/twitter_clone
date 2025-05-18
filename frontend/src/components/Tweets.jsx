import React, { useState, useEffect } from 'react';
import api from '../api';
import CreateTweetForm from './CreateTweetForm';

const TweetList = () => {
    const [tweets, setTweets] = useState([]);

    const fetchTweets = async () => {
        try {
            const response = await api.get('/tweets');
            setTweets(response.data.tweets);
        } catch (error) {
            console.error("Error fetching tweets", error);
        }
    };

    const addTweet = async (tweetUsername, tweetText) => {
    try {
        await api.post('/tweets', { username: tweetUsername, text: tweetText });
      fetchTweets();  // Refresh the list after creating a tweet
    } catch (error) {
        console.error("Error creating tweet", error);
    }
    };

    useEffect(() => {
        fetchTweets();
    }, []);

    return ( 
        <div>
            <ul>
                {/* tweets */}
                {tweets.map((tweet, index) => (
                    <li key={index}>{tweet.username} tweeted: {tweet.text}</li>
                ))}
            </ul>
            <CreateTweetForm addTweet={addTweet}/>
        </div>
    );
}
export default TweetList;