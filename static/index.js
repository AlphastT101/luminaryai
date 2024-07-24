// on img generate button click
document.getElementById('image-gen-btn').addEventListener('click', async function() {
    await generateImage();
});

async function generateImage() {
    const prompt = document.getElementById('promptInput').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const model = document.getElementById('modelInput').value;
    const img = document.getElementById('generatedImage');
    const btn = document.getElementById('image-gen-btn');
    const loading = document.getElementById('loading'); // Get loading element

    function setUIBusyState(isBusy) {
        btn.disabled = isBusy; // Disable button
        btn.style.display = isBusy ? 'none' : 'inline-block';
        loading.style.display = isBusy ? 'inline-block' : 'none'; // Show loading element
    }

    setUIBusyState(true);

    fetch('/v1/images/generations', {
        method: 'POST',
        body: JSON.stringify({ 
            model: model,
            prompt: prompt
        }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        }
    })
    .then(async response => {
        if (!response.ok) {
            const responseText = await response.text();
            throw new Error(`Request failed: (${response.status} ${response.statusText}) ${responseText}`);
        }

        return response.json(); // temporary workaround
    })

    .then(response => {
        img.src = response.data[0].url;
        img.style.display = 'block';
        setUIBusyState(false);
    })

    .catch(error => {
        console.error(error);
        setUIBusyState(false);
    });
}