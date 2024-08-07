// on img generate button click
document.getElementById('send').addEventListener('click', async function() {
    await process_request();
});
const promptInput = document.getElementById('promptInput');
promptInput.addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        process_request();
    }
});
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

let messages = [];

async function process_request() {
    const prompt = document.getElementById('promptInput').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const model = document.getElementById('modelInput').value;
    const img = document.getElementById('generatedImage');
    const btn = document.getElementById('send');
    const loading = document.getElementById('loading');
    const errorWindow = document.getElementById('errorWindow');
    const chatHistory = document.querySelector('.chat-history'); // Select parent container

    const text_models = [
        'gpt-4o', 'command-r-plus-online', 'openchat-7b', 'openchat-3.5-7b',
        'qwen-2-7b-instruct', 'phi-3-mini-128k-instruct',
        'phi-3-medium-128k-instruct', 'llama-3-8b-instruct', 'gemma-7b-it',
        'nous-capybara-7b', 'mythomist-7b', 'toppy-m-7b', 'zephyr-7b-beta',
        'mistral-7b-instruct'
    ];

    function setUIBusyState(isBusy) {
        btn.style.display = isBusy ? 'none' : 'inline-block';
        loading.style.display = isBusy ? 'inline-block' : 'none';
    }

    function showError(message) {
        errorWindow.textContent = message;
        errorWindow.classList.add('show');
        setTimeout(() => {
            errorWindow.classList.remove('show');
        }, 6000); // Hide after 6 seconds
    }

    setUIBusyState(true);

    try {
        if (!apiKey || !prompt) {
            throw new Error("You must set your API key and a message to get a response.");
        }

        const newUserDiv = document.createElement('div');
        newUserDiv.className = 'text-user';

        newUserDiv.innerHTML = `
            <i class="fa-solid fa-user"></i> You:
            <p>${prompt}</p>
        `;
        chatHistory.appendChild(newUserDiv);

        if (text_models.includes(model)) {
            messages.push({ "role": "user", "content": prompt });
        }

        const requestUrl = text_models.includes(model) ? 'v1/chat/completions' : '/v1/images/generations';
        const requestBody = text_models.includes(model) 
            ? JSON.stringify({ model: model, messages: messages })
            : JSON.stringify({ model: model, prompt: prompt });

        document.getElementById('promptInput').value = ''; // Clear input after sending

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
            messages.push({ "role": "assistant", "content": responseData.response });
            const newResponseDiv = document.createElement('div');
            newResponseDiv.className = 'text-response';

            newResponseDiv.innerHTML = `
                <i class="fa-solid fa-robot"></i> AI:
                <p>${responseData.response}</p>
            `;
            chatHistory.appendChild(newResponseDiv);
        } else {
            const newResponseDiv = document.createElement('div');
            newResponseDiv.className = 'image-response';

            newResponseDiv.innerHTML = `
                <i class="fa-solid fa-robot"></i> AI:
                <p>Here is your requested image: </p>
                <img src="${responseData.data[1].localhost}">
            `;
            chatHistory.appendChild(newResponseDiv);
        }
    } catch (error) {
        console.error(error);
        showError(error.message);
    } finally {
        setUIBusyState(false);
    }
}