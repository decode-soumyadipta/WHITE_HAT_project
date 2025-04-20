/**
 * SHIELD - Security Hub for Intelligent Entry-Level Defense
 * Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set up filter functionality for vulnerability and test case pages
    setupFilters();
    
    // Add card hover effects
    applyCardHoverEffects();
    
    // Initialize tooltips and popovers if Bootstrap is available
    initializeBootstrapComponents();
    
    // Initialize Matrix effect for login page
    initMatrixEffect();
    
    // Add pulsing effect to the login button
    const loginBtn = document.querySelector('.btn-login');
    if (loginBtn) {
        loginBtn.addEventListener('mouseenter', function() {
            this.classList.add('pulse');
        });
        loginBtn.addEventListener('mouseleave', function() {
            this.classList.remove('pulse');
        });
    }
});

/**
 * Set up filter functionality for vulnerability and test case pages
 */
function setupFilters() {
    // Vulnerability severity filters
    const severityFilters = document.querySelectorAll('input[id$="Check"]');
    
    severityFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            applyFilters();
        });
    });
    
    // Apply filters function
    function applyFilters() {
        // For demonstration purposes, we're just logging
        console.log('Filters applied');
        
        // In a real implementation, this would filter table rows
        // based on the selected filter checkboxes
    }
}

/**
 * Apply hover effects to cards with the card-hover class
 */
function applyCardHoverEffects() {
    const cards = document.querySelectorAll('.card:not(.card-hover)');
    
    cards.forEach(card => {
        card.classList.add('card-hover');
    });
}

/**
 * Initialize Bootstrap components like tooltips and popovers
 */
function initializeBootstrapComponents() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

/**
 * Run a test case and handle UI updates
 * @param {string} testCaseId - The ID of the test case to run
 */
function runTest(testCaseId) {
    const button = document.getElementById('runTestBtn');
    
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running...';
        
        // Simulate a test run with a delay
        setTimeout(function() {
            // This would typically be an AJAX call to the server
            console.log(`Running test case ${testCaseId}`);
            
            // Simulate completion
            alert('Test execution completed! Page will reload with results.');
            window.location.reload();
        }, 3000);
    }
}

/**
 * Initialize the AI Agent Automation page
 */
function initAIAgentPage() {
    const runAssessmentBtn = document.getElementById('runAssessmentBtn');
    
    if (runAssessmentBtn) {
        runAssessmentBtn.addEventListener('click', function(event) {
            // Only handle click if not part of a form submission
            if (!event.target.form) {
                event.preventDefault();
                
                const techStackField = document.getElementById('tech_stack');
                if (techStackField && techStackField.value.trim() === '') {
                    alert('Please enter a technology stack to analyze.');
                    techStackField.focus();
                    return;
                }
                
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Running Assessment...';
                
                // This would be replaced with actual form submission
                setTimeout(() => {
                    this.form.submit();
                }, 1000);
            }
        });
    }
}

/**
 * Initialize the Matrix effect for the login page
 */
function initMatrixEffect() {
    const loginPage = document.querySelector('.login-card');
    
    if (loginPage) {
        // Create matrix background container
        const matrixBg = document.createElement('div');
        matrixBg.className = 'matrix-bg';
        document.body.appendChild(matrixBg);
        
        // Add binary elements
        for (let i = 0; i < 50; i++) {
            createBinaryElement(matrixBg);
        }
        
        // Add animation to body
        document.body.classList.add('dark-theme');
    }
}

/**
 * Create a binary element for the matrix effect
 * @param {HTMLElement} container - The container element
 */
function createBinaryElement(container) {
    const element = document.createElement('div');
    element.className = 'binary-element';
    
    // Random binary string
    const binaryChars = ['0', '1'];
    let binaryString = '';
    
    for (let i = 0; i < 8; i++) {
        binaryString += binaryChars[Math.floor(Math.random() * 2)];
    }
    
    element.textContent = binaryString;
    
    // Random position
    const posX = Math.random() * window.innerWidth;
    const posY = Math.random() * window.innerHeight;
    element.style.left = `${posX}px`;
    element.style.top = `${posY}px`;
    
    // Random animation delay
    element.style.animationDelay = `${Math.random() * 5}s`;
    
    container.appendChild(element);
    
    // Remove and recreate after animation
    setTimeout(() => {
        element.remove();
        createBinaryElement(container);
    }, 3000 + (Math.random() * 2000));
} 