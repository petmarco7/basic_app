import React, { useState, useEffect } from 'react';
import './Annotation.css';

const Annotation = () => {
  const url = 'http://localhost:8080/';
  const [text, setText] = useState('');          // Holds text fetched from backend
  const [selectedWords, setSelectedWords] = useState([]); // Holds selected words with positions
  const [words, setWords] = useState([]);        // Holds text split into words
  const [whitespaces, setWhitespaces] = useState([]); // Holds whitespaces between words
  const [selectedLabel, setSelectedLabel] = useState(''); // Holds currently selected label ("Person" or "Organization")
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectionRange, setSelectionRange] = useState({ start: null, end: null });

  // // Function to split text into words and punctuation
  // const splitText = (text) => {return text.match(/\w+|[^\w\s]/g);};

  // Fetch text from backend on component mount
  useEffect(() => {
    const fetchText = async () => {
      try {
        const response = await fetch(url + 'text/');
        const data = await response.json();
        setText(data.text);
        setWords(data.words);
        setWhitespaces(data.whitespaces);
        // Set the first annotations
        setSelectedWords(data.annotations);
      } catch (error) {
        console.error('Error fetching text:', error);
      }
    };
    fetchText();
  }, []);

  // Handle label selection
  const handleLabelSelection = (label) => {

    // If the same label is clicked again, deselect it
    if (selectedLabel === label) {
      setSelectedLabel('');
      return;
    }

    // Set the selected label
    setSelectedLabel(label);
  };

  const handleMouseDown = (index) => {
    setIsSelecting(true);
    setSelectionRange({ start: index, end: index });
  };

  const handleMouseOver = (index) => {
    if (isSelecting) {
      setSelectionRange((prevRange) => ({ ...prevRange, end: index }));
    }
  };

  const handleMouseUp = (index) => {
    if (isSelecting) {
      const { start, end } = selectionRange;
      const selectedIndices = [Math.min(start, end), Math.max(start, end)];
      // Join selected words with whitespaces
      const selectedText = words.slice(selectedIndices[0], selectedIndices[1] + 1).map((word, i) => word + (whitespaces[selectedIndices[0] + i]||'')).join('').trimEnd();

      const position = {
        word: selectedText,
        start: text.indexOf(selectedText),
        end: text.indexOf(selectedText) + selectedText.length - 1,
        label: selectedLabel,
        from: selectedIndices[0],
        to: selectedIndices[1]
      };

      const alreadySelected = selectedWords.some(
        (w) => w.from <= index && w.to >= index
      );

      if (alreadySelected) {
        setSelectedWords(selectedWords.filter(w => w.to < index || w.from > index));
        return;
      }

      if (!selectedLabel) {
        alert('Please select a label before tagging a word.');
        return;
      }

      setSelectedWords([...selectedWords, position]);

    }
    setIsSelecting(false);
    setSelectionRange({ start: null, end: null });
  };

  // Handle word submit
  const handleWordSubmit = async (e) => {
    e.preventDefault();
    console.log('Selected words:');
    console.log(selectedWords);
    try {
      const response = await fetch(url + 'text_highlight/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Return a dict of the form word:{word:..,start:..,end:..} of selected words
        body: JSON.stringify({ text: text, annotations: selectedWords }),
      });
      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error('Error submitting text:', error);
    }
  };

  // Adjust `isHighlighted` function to check for range
  const isHighlightedRange = (index) => {
    return selectedWords.find(w => w.from <= index && w.to >= index);
  }

  // Adjust rendering to group adjacent selections
  const renderWords = () => {
    const elements = [];
    let i = 0;

    while (i < words.length) {
      const currentIndex = i;
      const highlightedRange = isHighlightedRange(currentIndex);

      if (highlightedRange) {
        // Render selected words as a single span
        const rangeText = words.slice(highlightedRange.from, highlightedRange.to + 1).map((word, i) => word + (whitespaces[highlightedRange.from + i]||'')).join('').trimEnd();

        elements.push(
          <span
            key={currentIndex}
            className={`word selected ${highlightedRange.label.toLowerCase()}`}
            onMouseDown={() => handleMouseDown(highlightedRange.from)}
            onMouseOver={() => handleMouseOver(highlightedRange.to)}
            onMouseUp={() => handleMouseUp(highlightedRange.to)}
          >
            {rangeText}
          </span>
        );
        i = highlightedRange.to; // Skip to the end of this selection
      } else {
        // Render non-selected word as usual
        elements.push(
          <span
            key={currentIndex}
            className="word"
            onMouseDown={() => handleMouseDown(currentIndex)}
            onMouseOver={() => handleMouseOver(currentIndex)}
            onMouseUp={() => handleMouseUp(currentIndex)}
          >
            {words[i]}
          </span>
        );
      }
      i++;
    }

    return elements;
  };

  return (
    <div>
      <h1>Annotations</h1>
      <p>Welcome to the annotations page</p>

      <br></br>
      <br></br>
      <br></br>

      <div className="label-buttons">
        <button id="person-button" className={`label-button ${selectedLabel === 'Person' ? 'active' : ''}`} onClick={() => handleLabelSelection('Person')}>
          Person
        </button>
        <button id="organization-button" className={`label-button ${selectedLabel === 'Organization' ? 'active' : ''}`} onClick={() => handleLabelSelection('Organization')}>
          Organization
        </button>
      </div>

      <br></br>
      <br></br>
      <br></br>
      <br></br>

      <form className="selected-words-form">
        <div className="selected-words">
          {renderWords()}
        </div>
        <br></br>
        <button type="submit" className="submit-button" onClick={handleWordSubmit}>Submit</button>
      </form>

    </div>
  );
}

export default Annotation;
