import React, { Component, createRef } from 'react';
import ReactDOM from 'react-dom';
import '@cloudscape-design/global-styles/index.css';

// Automatically add visual refresh class to the body
if (typeof document !== 'undefined') {
  document.body.classList.add('awsui-visual-refresh');
}


// Import all Cloudscape components from the library
import * as Components from './lib/components';

// Individual Portal component to mount a single native DOM child inside the React tree
class ChildPortal extends Component {
  constructor(props) {
    super(props);
    this.containerRef = createRef();
  }
  componentDidMount() {
    if (this.props.child) {
      this.containerRef.current.appendChild(this.props.child);
    }
  }
  render() {
    return React.createElement('div', { 
      ref: this.containerRef, 
      style: { display: 'contents' } 
    });
  }
}

// Convert kebab-case attributes to camelCase props
function getPropsFromAttributes(element) {
  const props = {};
  for (const attr of element.attributes) {
    let name = attr.name;
    // Map kebab-case to camelCase (e.g. header-text -> headerText)
    name = name.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    
    let val = attr.value;
    if (val === '') {
      props[name] = true;
    } else {
      try {
        // Try parsing JSON values (e.g. lists, objects)
        props[name] = JSON.parse(val);
      } catch (e) {
        props[name] = val;
      }
    }
  }
  return props;
}

// Map custom events for Cloudscape callbacks
const callbackNames = [
  'onClick', 'onChange', 'onDismiss', 'onFollow', 'onTabChange', 'onInput', 'onBlur', 'onFocus',
  'onHeaderClick', 'onItemClick', 'onSelectionChange', 'onToggle', 'onClose', 'onOpen', 'onNavigate'
];

function registerWebComponent(tagName, ReactComponent) {
  customElements.define(tagName, class extends HTMLElement {
    constructor() {
      super();
      this.mountPoint = null;
      this.originalChildren = [];
    }

    connectedCallback() {
      // Defer execution until the browser parser completes parsing children
      this._timeout = setTimeout(() => {
        if (!this.mountPoint) {
          this.originalChildren = Array.from(this.childNodes).filter(node => 
            node.nodeType !== 3 || node.textContent.trim() !== ''
          );
          this.innerHTML = '';

          this.mountPoint = document.createElement('div');
          this.mountPoint.style.display = 'contents';
          this.appendChild(this.mountPoint);

          // Listen for attribute changes dynamically
          this.observer = new MutationObserver(() => this.renderComponent());
          this.observer.observe(this, { attributes: true });
        }
        this.renderComponent();
      }, 0);
    }

    disconnectedCallback() {
      if (this._timeout) {
        clearTimeout(this._timeout);
      }
      if (this.observer) {
        this.observer.disconnect();
      }
      if (this.mountPoint) {
        ReactDOM.unmountComponentAtNode(this.mountPoint);
      }
    }
    renderComponent() {
      const props = getPropsFromAttributes(this);

      // Bind all common callbacks to dispatch custom DOM events
      callbackNames.forEach(cbName => {
        const eventName = cbName.slice(2).toLowerCase(); // onClick -> click
        props[cbName] = (e) => {
          const customEvent = new CustomEvent(eventName, {
            detail: e ? (e.detail || e) : null,
            bubbles: true,
            composed: true
          });
          this.dispatchEvent(customEvent);
        };
      });

      // Special handling for Table component column cell renderers
      if (ReactComponent === Components.Table && props.columnDefinitions) {
        props.columnDefinitions = props.columnDefinitions.map(col => {
          if (!col.cell) {
            return {
              ...col,
              cell: (item) => {
                const val = item[col.id];
                if (typeof val === 'string' && (val.includes('<') || val.includes('>'))) {
                  return React.createElement('span', { 
                    dangerouslySetInnerHTML: { __html: val },
                    style: { display: 'contents' }
                  });
                }
                return val !== undefined ? val : '';
              }
            };
          }
          return col;
        });
      }

      const childrenPortals = this.originalChildren.map((child, index) => {
        return React.createElement(ChildPortal, { key: index, child: child });
      });

      ReactDOM.render(
        React.createElement(
          ReactComponent,
          props,
          ...childrenPortals
        ),
        this.mountPoint
      );
    }
  });
}

// Helper to convert PascalCase/CamelCase to kebab-case
function camelToKebab(str) {
  return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
}

// Dynamically register all exported React components as Web Components
Object.keys(Components).forEach(name => {
  const Comp = Components[name];
  // Filter for valid React component functions/classes
  if (typeof Comp === 'function' || (typeof Comp === 'object' && Comp !== null)) {
    // Avoid double registering and check for standard components
    const kebabName = camelToKebab(name);
    const tagName = `cloudscape-${kebabName}`;
    
    // Skip internal, non-visual utility exports or interface placeholders
    if (kebabName === 'interfaces' || name.startsWith('use') || name.endsWith('Context')) {
      return;
    }
    
    try {
      registerWebComponent(tagName, Comp);
    } catch (e) {
      console.warn(`Could not register component ${tagName}:`, e);
    }
  }
});

console.log('Cloudscape Web Components Adapter Initialized!');
