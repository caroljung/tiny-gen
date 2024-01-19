"use client"; 

import './style.css'
import { useState } from 'react';

const Home: React.FC = () => {
  const [repoUrl, setRepoUrl] = useState<string>('');
  const [prompt, setPrompt] = useState<string>('');
  const [diffResponse, setDiffResponse] = useState<string | undefined>();


  const handleSubmit = async (e: React.FormEvent<EventTarget>) => {
    e.preventDefault();
    setDiffResponse('Loading...\n');

    try {
      const response = await fetch('/api/generate-diff', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Accept': 'text/event-stream'
          },
          body: JSON.stringify({ repoUrl, prompt: prompt })
      });

      const reader = response?.body?.getReader();
      const decoder = new TextDecoder();

      while (reader && true) {
          const { done, value } = await reader.read();
          if (done) break;
          const decodedContent = decoder.decode(value, { stream: true });
          console.log(decodedContent);
          setDiffResponse(prev => prev + decodedContent);
      }
    } catch (error) {
        console.error('Error:', error);
        setDiffResponse('Error fetching data.');
    }
  };

  return (
    <div style={{ paddingTop: '100px', textAlign: 'center'}}>
      <h1>tiny-gen 🤏🏼</h1> 
      <div className="wrapper">
        <div className="container">
            <form onSubmit={handleSubmit}>
                <label htmlFor="repoUrl">Code Repository Url:</label>
                <input
                    type="text"
                    id="repoUrl"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="Enter public github repo URL"
                />
                
                <label htmlFor="prompt">Command Prompt:</label>
                <textarea
                    id="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="What change should I make to the repo?"
                />

                <button type="submit">✨ Generate diff ✨</button>
            </form>
        </div>
        <div className="diff">
          <pre className="codeDiff">{diffResponse}</pre>
        </div>
      </div>
    </div>
);
};

export default Home;
