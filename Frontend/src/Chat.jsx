import "./Chat.css";
import { MyContext } from "./MyContext";
import React, { useContext, useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css"; // Change to github-dark if you want dark theme

function Chat() {
  const { newChat, prevChats, reply } = useContext(MyContext);
  const [latestReply, setLatestReply] = useState(null);

  useEffect(() => {
    if (!reply) {
      setLatestReply(null);
      return;
    }

    if (!Array.isArray(prevChats) || prevChats.length === 0) return;

    const content = reply.split(" ");
    let idx = 0;

    const interval = setInterval(() => {
      setLatestReply(content.slice(0, idx + 1).join(" "));
      idx++;
      if (idx >= content.length) clearInterval(interval);
    }, 40);

    return () => clearInterval(interval);
  }, [prevChats, reply]);

  const chatsArray = Array.isArray(prevChats) ? prevChats : [];

  return (
    <div className="chat-container">
      {newChat && chatsArray.length === 0 && (
        <h2 className="start-chat-text">Start a new Chat</h2>
      )}

      <div className="chats">
        {chatsArray.map((chat, index) => (
          <div
            key={index}
            className={chat.role === "user" ? "userDiv" : "aiDiv"}
          >
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
              {chat.content}
            </ReactMarkdown>
          </div>
        ))}

        {/* Typing effect for latest GPT reply */}
        {latestReply !== null && (
          <div className="aiDiv" key="typing">
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
              {latestReply}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

export default Chat;
