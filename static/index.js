//// Settings button start ////
document.getElementById('settings').addEventListener('click', function() {
    const overlay = document.getElementById('overlay');
    const settingsWindow = document.getElementById('settingsWindow');

    overlay.classList.add('show');
    settingsWindow.classList.add('show');
});

document.getElementById('overlay').addEventListener('click', function() {
    const overlay = document.getElementById('overlay');
    const settingsWindow = document.getElementById('settingsWindow');

    overlay.classList.remove('show');
    settingsWindow.classList.remove('show');
});

document.getElementById('closeSettings').addEventListener('click', function() {
    const overlay = document.getElementById('overlay');
    const settingsWindow = document.getElementById('settingsWindow');

    overlay.classList.remove('show');
    settingsWindow.classList.remove('show');
});
//// settings button end ////





//// API requests start ////
const text_models = [
    'gpt-4', 'gpt-4-turbo', 'gpt-3.5', 'gpt-3.5-turbo',
    'llama-3','llama-3.1', 'gemma-2', 'mistral', 'gpt-4o',
    'command-r-plus-online'
];

document.getElementById('send').addEventListener('click', async function() {
    await process_request();
});

const promptInput = document.getElementById('promptInput');

promptInput.addEventListener('input', function () {
    // Reset the height to calculate the new scrollHeight
    this.style.height = 'auto';
    // Set the height to the scrollHeight, but limit it to a max height
    this.style.height = `${Math.min(this.scrollHeight, 242)}px`;
});

promptInput.addEventListener('keypress', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevents the default behavior of the Enter key
        process_request();
    }
});

async function formatText(answer) {

    answer = escapeHTML(answer);
    // Code Block: ```language code ```
    answer = answer.replace(/```(\w+)?\n([\s\S]*?)```/g,
        '<pre class="code-block-wrapper"><button class="copy-btn">Copy</button><code class="language-$1">$2</code></pre>');

    // Combining Formatting: __**Bold and Underlined**__
    answer = answer.replace(/__\*\*(.*?)\*\*__/g, '<u><strong>$1</strong></u>');

    // Bold + Italic: ***text***
    answer = answer.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');

    // Bold: **text**
    answer = answer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text* or _text_
    answer = answer.replace(/(\*|_)(.*?)\1/g, '<em>$2</em>');

    // Underline: __text__
    //answer = answer.replace(/__(.*?)__/g, '<u>$1</u>');

    // Strikethrough: ~~text~~
    answer = answer.replace(/~~(.*?)~~/g, '<del>$1</del>');

    // Inline Code: `code`
    answer = answer.replace(/`([^`]+)`/g, '<code style="background: #2e2533;padding: 3px;color:white;">$1</code>');

    // Block Quotes: > text
    answer = answer.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');
    answer = answer.replace(/^>> (.*$)/gim, '<blockquote><blockquote>$1</blockquote></blockquote>');

    // Ordered Lists: 1. item
    answer = answer.replace(/^\d+\.\s(.*$)/gim, '<li>$1</li>');
    answer = answer.replace(/(<\/li>\n<li>)/g, '</li><li>');
    answer = answer.replace(/(<li>.*<\/li>)/g, '<ol>$1</ol>');

    // Unordered Lists: - item or + item or * item
    answer = answer.replace(/^[-\*\+]\s(.*$)/gim, '<li>$1</li>');
    answer = answer.replace(/(<\/li>\n<li>)/g, '</li><li>');
    answer = answer.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');

    // Hyperlinks: [text](url)
    answer = answer.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    return answer;
}

function escapeHTML(html) {
    return html
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

let messages = [];
async function process_request() {
    const prompt = document.getElementById('promptInput').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const model = document.getElementById('modelInput').value;
    const chatHistory = document.querySelector('.chat-history');
    const btn = document.getElementById('send');
    const loading = document.getElementById('loading');
    const errorWindow = document.getElementById('errorWindow');
    // disable buttons
    function setUIBusyState(isBusy) {
        btn.style.display = isBusy ? 'none' : 'inline-block';
        loading.style.display = isBusy ? 'inline-block' : 'none';
    }
    // error message
    function showError(message) {
        errorWindow.textContent = message;
        errorWindow.classList.add('show');
        setTimeout(() => {
            errorWindow.classList.remove('show');
        }, 6000); // Hide after 6 seconds
    }

    setUIBusyState(true); // disable btn

    try {
        if (!apiKey || !prompt) {
            throw new Error("You must set your API key and a message to get a response.");
        }

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });

        const newUserDiv = document.createElement('div');
        newUserDiv.className = 'text-user';
        newUserDiv.dataset.aos = 'fade'; // Set data-aos attribute

        const formatted_prompt = await formatText(prompt);
        newUserDiv.innerHTML = `
            <i class="fa-solid fa-user"></i> You:
            <p>${formatted_prompt}</p>
        `;
        chatHistory.appendChild(newUserDiv);
        Prism.highlightAll();

        if (text_models.includes(model)) {
            messages.push({ "role": "user", "content": prompt });
        }

        const requestUrl = text_models.includes(model) ? '/v1/chat/completions' : '/v1/images/generations';
        const requestBody = text_models.includes(model)
            ? JSON.stringify({ model: model, messages: messages })
            : JSON.stringify({ model: model, prompt: prompt });

        document.getElementById('promptInput').value = ''; // Clear input after sending
        promptInput.style.height = '38px'; // Reset to default height
        const requestHeaders = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        };

        const response = await fetch(requestUrl, {
            method: 'POST',
            body: requestBody,
            headers: requestHeaders
        });

        if (!response.ok) {
            const responseText = await response.text();
            throw new Error(`Error: ${response.statusText}, ${responseText}`);
        }

        const responseData = await response.json();

        if (text_models.includes(model)) {
            let answer = responseData.response;
            messages.push({ "role": "assistant", "content": answer });

            const newResponseDiv = document.createElement('div');
            newResponseDiv.className = 'text-response';
            newResponseDiv.dataset.aos = 'fade'; // Set data-aos attribute

            const formatted_answer = await formatText(answer);
            newResponseDiv.innerHTML = `
                <i class="fa-duotone fa-solid fa-microchip-ai" style="font-size: 25px;"></i> AI:
                <p>${formatted_answer}</p>
            `;
            chatHistory.appendChild(newResponseDiv);
            Prism.highlightAll();
        }
        else {
            const newResponseDiv = document.createElement('div');
            newResponseDiv.className = 'image-response';
            newResponseDiv.dataset.aos = 'fade'; // Set data-aos attribute

            newResponseDiv.innerHTML = `
                <i class="fa-duotone fa-solid fa-microchip-ai" style="font-size: 25px;"></i> AI:
                <p>Here is your requested image: </p>
                <img src="${responseData.data[0].url}">
            `;
            chatHistory.appendChild(newResponseDiv);
        }

        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });

    } catch (error) {
        console.error(error);
        showError(error.message);
    } finally {
        setUIBusyState(false);
    }
}


document.addEventListener('click', function(e) {
    if (e.target.classList.contains('copy-btn')) {
        const codeBlock = e.target.nextElementSibling.innerText;
        
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(codeBlock).then(() => {
                e.target.textContent = 'Copied!';
                setTimeout(() => {
                    e.target.textContent = 'Copy';
                }, 5000);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        } else {
            // Fallback for non-secure contexts
            const tempTextArea = document.createElement('textarea');
            tempTextArea.value = codeBlock;
            document.body.appendChild(tempTextArea);
            tempTextArea.select();
            try {
                document.execCommand('copy');
                e.target.textContent = 'Copied!';
                setTimeout(() => {
                    e.target.textContent = 'Copy';
                }, 5000);
            } catch (err) {
                console.error('Failed to copy: ', err);
            }
            document.body.removeChild(tempTextArea);
        }
    }
});
