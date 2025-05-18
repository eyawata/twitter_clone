import React from 'react';
import './App.css';
import TweetList from './components/Tweets';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Twitter App</h1>
      </header>
      <main>
        <TweetList />
      </main>
    </div>
  );
};

export default App;