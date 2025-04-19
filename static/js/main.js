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