import { BaseEl } from '/chat/static/js/base.js';
import { html, css } from '/chat/static/js/lit-core.min.js';

class ComputerUseViewer extends BaseEl {
  static properties = {
    refreshRate: { type: Number },
    containerStatus: { type: String },
    isFullscreen: { type: Boolean }
  };

  static styles = css`
    :host {
      display: block;
      background: var(--component-bg, var(--background-color));
      color: var(--component-text, var(--text-color));
      border-radius: 8px;
      overflow: hidden;
      margin: 1rem 0;
    }
    
    .container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    
    .toolbar {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem;
      background: rgba(0,0,0,0.2);
    }
    
    .toolbar button {
      margin-left: 0.5rem;
      padding: 0.25rem 0.5rem;
      background: var(--link-color);
      border: none;
      border-radius: 4px;
      color: white;
      cursor: pointer;
    }
    
    .screen {
      flex: 1;
      min-height: 400px;
      border: 1px solid rgba(255,255,255,0.1);
      background: #000;
      position: relative;
    }
    
    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
    
    .status {
      color: #aaa;
      padding: 0.5rem;
      font-size: 0.8rem;
    }
    
    .fullscreen {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
      border-radius: 0;
    }
    
    .fullscreen .screen {
      min-height: calc(100vh - 50px);
    }
  `;

  constructor() {
    super();
    this.refreshRate = 2000; // ms
    this.containerStatus = 'unknown';
    this.isFullscreen = false;
    this.interval = null;
  }
  
  connectedCallback() {
    super.connectedCallback();
    this.checkContainerStatus();
    this.interval = setInterval(() => this.checkContainerStatus(), this.refreshRate);
  }
  
  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.interval) {
      clearInterval(this.interval);
    }
  }
  
  async checkContainerStatus() {
    try {
      const response = await fetch('/computer_use/api/status');
      const data = await response.json();
      this.containerStatus = data.status;
    } catch (error) {
      this.containerStatus = 'error';
      console.error('Failed to check container status:', error);
    }
  }
  
  async startContainer() {
    try {
      this.containerStatus = 'starting';
      const response = await fetch('/computer_use/api/start', { method: 'POST' });
      const data = await response.json();
      if (data.status === 'ok') {
        this.containerStatus = 'running';
      } else {
        this.containerStatus = 'error';
      }
    } catch (error) {
      this.containerStatus = 'error';
      console.error('Failed to start container:', error);
    }
  }
  
  async stopContainer() {
    try {
      this.containerStatus = 'stopping';
      const response = await fetch('/computer_use/api/stop', { method: 'POST' });
      const data = await response.json();
      if (data.status === 'ok') {
        this.containerStatus = 'stopped';
      } else {
        this.containerStatus = 'error';
      }
    } catch (error) {
      this.containerStatus = 'error';
      console.error('Failed to stop container:', error);
    }
  }
  
  toggleFullscreen() {
    this.isFullscreen = !this.isFullscreen;
  }
  
  render() {
    return html`
      <div class="container ${this.isFullscreen ? 'fullscreen' : ''}">
        <div class="toolbar">
          <div>
            <span>Computer Use Status: ${this.containerStatus}</span>
          </div>
          <div>
            ${this.containerStatus !== 'running' ? 
              html`<button @click=${this.startContainer}>Start</button>` : 
              html`<button @click=${this.stopContainer}>Stop</button>`
            }
            <button @click=${this.toggleFullscreen}>
              ${this.isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            </button>
          </div>
        </div>
        
        <div class="screen">
          ${this.containerStatus === 'running' ?
            html`<iframe src="http://localhost:6080/vnc.html?autoconnect=true" frameborder="0"></iframe>` :
            html`<div class="status">
              ${this.containerStatus === 'starting' ? 'Starting computer use container...' :
                this.containerStatus === 'stopping' ? 'Stopping computer use container...' :
                this.containerStatus === 'stopped' ? 'Container stopped. Click Start to launch computer use VM.' :
                'Container not running. Click Start to launch computer use VM.'}
            </div>`
          }
        </div>
      </div>
    `;
  }
}

customElements.define('computer-use-viewer', ComputerUseViewer);

// Register command handlers
window.registerCommandHandler('computer_start', (data) => {
  if (data.event === 'result') {
    return html`<div>Computer Use VM started. Use the viewer to interact or issue computer use commands.</div>`;
  }
  return null;
});

window.registerCommandHandler('computer_screenshot', (data) => {
  // The screenshot is added to chat via format_image_message
  // No need to return anything here
  return null;
});
