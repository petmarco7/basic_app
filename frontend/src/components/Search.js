import React, { useState } from 'react';
import './Search.css';

const Search = () => {
  const url = 'http://localhost:8080/';
  const [inputText, setInputText] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(url + 'submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error('Error submitting text:', error);
    }
  };

  return (
    <div>
      <h1>Search</h1>
      <p>Welcome to the search page</p>
      <br></br>
      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter text here"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="input-field"
        />
        <button type="submit" className="submit-button">Submit</button>
      </form>
    </div>
  );
}

export default Search;
