const loaderss = ['pyramid', 'hex_bricks', 'console_loading', 'loader_cube', 'loader_box_fall']
const loaders = ['hex_bricks']
const loading_code = {
    "pyramid": `
        <div class="pyramid-loader">
            <div class="wrapper">
            <span class="side side1"></span>
            <span class="side side2"></span>
            <span class="side side3"></span>
            <span class="side side4"></span>
            <span class="shadow"></span>
            </div>  
        </div>`,



    'console_loading':`
        <div class="loader-container">
            <div class="terminal-loader">
            <div class="terminal-header">
                <div class="terminal-title">Status</div>
                <div class="terminal-controls">
                <div class="control close"></div>
                <div class="control minimize"></div>
                <div class="control maximize"></div>
                </div>
            </div>
            <div class="text">Loading...</div>
            </div>
        </div>`,



    'loader_cube':`
        <div class="loader_main_cube">
            <div class="loader_cube loader_cube--color"></div>
            <div class="loader_cube loader_cube--glowing"></div>
        </div>`,



    'loader_box_fall':`
        <div class="loader_box_fall">
        <div class="box box-1">
            <div class="side-left"></div>
            <div class="side-right"></div>
            <div class="side-top"></div>
        </div>
        <div class="box box-2">
            <div class="side-left"></div>
            <div class="side-right"></div>
            <div class="side-top"></div>
        </div>
        <div class="box box-3">
            <div class="side-left"></div>
            <div class="side-right"></div>
            <div class="side-top"></div>
        </div>
        <div class="box box-4">
            <div class="side-left"></div>
            <div class="side-right"></div>
            <div class="side-top"></div>
        </div>
        </div>`,



        "hex_bricks": `
            <div class="socket">
                <div class="gel center-gel">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c1 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c2 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c3 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c4 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c5 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c6 r1">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                
                <div class="gel c7 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                
                <div class="gel c8 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c9 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c10 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c11 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c12 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c13 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c14 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c15 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c16 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c17 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c18 r2">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c19 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c20 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c21 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c22 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c23 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c24 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c25 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c26 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c28 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c29 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c30 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c31 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c32 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c33 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c34 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c35 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c36 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
                <div class="gel c37 r3">
                    <div class="hex-brick h1"></div>
                    <div class="hex-brick h2"></div>
                    <div class="hex-brick h3"></div>
                </div>
            </div>`
};



function startup_load() {


    const selected_loader = loaders[Math.floor(Math.random() * loaders.length)];
    const loader_code = loading_code[selected_loader] || '';

    const loadingDiv = document.createElement('div');
    loadingDiv.innerHTML = loader_code;
    document.body.appendChild(loadingDiv);

    // Ensure scrolling is re-enabled once the page is fully loaded
    window.addEventListener('load', () => {
        setTimeout(() => {
            loadingDiv.remove();
            document.getElementsByClassName("chat-history")[0].style.visibility = 'visible'
            document.getElementsByClassName("utils")[0].style.visibility = 'visible'
            document.getElementsByClassName("logo")[0].style.visibility = 'visible'

            document.getElementsByClassName("chat-history")[0].style.opacity = 1
            document.getElementsByClassName("utils")[0].style.opacity = 1
            document.getElementsByClassName("logo")[0].style.opacity = 1
        }, 2000); // Adjust delay as needed
    });
}

document.addEventListener('DOMContentLoaded', startup_load);