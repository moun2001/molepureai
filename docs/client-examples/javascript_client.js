/**
 * JavaScript Client SDK for Drug Interaction Prediction API
 * 
 * This module provides a convenient JavaScript interface for the Drug Interaction API.
 * Compatible with Node.js and modern browsers.
 */

class Drug {
    /**
     * Create a Drug object
     * @param {Object} data - Drug data
     * @param {string} data.drug_name - Name of the drug
     * @param {string} data.pharmacodynamic_class - Pharmacodynamic class
     * @param {number} data.logp - LogP value
     * @param {string} data.therapeutic_index - Therapeutic index (NTI or Non-NTI)
     * @param {string} data.transporter_interaction - Transporter interaction info
     * @param {number} data.plasma_protein_binding - Plasma protein binding percentage
     * @param {string} data.metabolic_pathways - Metabolic pathways
     */
    constructor(data) {
        this.drug_name = data.drug_name;
        this.pharmacodynamic_class = data.pharmacodynamic_class;
        this.logp = data.logp;
        this.therapeutic_index = data.therapeutic_index;
        this.transporter_interaction = data.transporter_interaction;
        this.plasma_protein_binding = data.plasma_protein_binding;
        this.metabolic_pathways = data.metabolic_pathways;
    }

    /**
     * Convert to plain object for API request
     * @returns {Object} Plain object representation
     */
    toJSON() {
        return {
            drug_name: this.drug_name,
            pharmacodynamic_class: this.pharmacodynamic_class,
            logp: this.logp,
            therapeutic_index: this.therapeutic_index,
            transporter_interaction: this.transporter_interaction,
            plasma_protein_binding: this.plasma_protein_binding,
            metabolic_pathways: this.metabolic_pathways
        };
    }
}

class InteractionPrediction {
    /**
     * Create an InteractionPrediction object
     * @param {Object} data - Prediction data from API
     */
    constructor(data) {
        this.drugA = {
            name: data.drug_pair.drug_a.name,
            class: data.drug_pair.drug_a.class,
            index: data.drug_pair.drug_a.index
        };
        this.drugB = {
            name: data.drug_pair.drug_b.name,
            class: data.drug_pair.drug_b.class,
            index: data.drug_pair.drug_b.index
        };
        this.severity = data.prediction.severity;
        this.confidence = data.prediction.confidence;
        this.riskLevel = data.prediction.risk_level;
        this.clinicalSignificance = data.clinical_significance;
        this.recommendation = data.recommendation;
        this.probabilityDistribution = data.probability_distribution;
    }

    /**
     * Get formatted interaction description
     * @returns {string} Formatted description
     */
    getDescription() {
        return `${this.drugA.name} + ${this.drugB.name}: ${this.severity} (${(this.confidence * 100).toFixed(1)}% confidence)`;
    }
}

class DrugInteractionAPIError extends Error {
    /**
     * Custom error for API-related issues
     * @param {string} message - Error message
     * @param {number} statusCode - HTTP status code
     * @param {Object} details - Additional error details
     */
    constructor(message, statusCode = null, details = null) {
        super(message);
        this.name = 'DrugInteractionAPIError';
        this.statusCode = statusCode;
        this.details = details;
    }
}

class DrugInteractionClient {
    /**
     * Create a Drug Interaction API client
     * @param {string} baseUrl - Base URL of the API
     * @param {Object} options - Client options
     * @param {number} options.timeout - Request timeout in milliseconds
     * @param {Object} options.headers - Additional headers
     */
    constructor(baseUrl = 'http://localhost:5000', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.timeout = options.timeout || 120000; // 120 seconds
        this.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DrugInteractionClient/1.0.0',
            ...options.headers
        };
    }

    /**
     * Make HTTP request with error handling
     * @private
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: 'GET',
            headers: this.headers,
            ...options
        };

        // Add timeout for fetch (if supported)
        if (typeof AbortController !== 'undefined') {
            const controller = new AbortController();
            config.signal = controller.signal;
            setTimeout(() => controller.abort(), this.timeout);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new DrugInteractionAPIError(
                    data.error || `HTTP ${response.status}`,
                    response.status,
                    data
                );
            }

            return data;
        } catch (error) {
            if (error instanceof DrugInteractionAPIError) {
                throw error;
            }
            throw new DrugInteractionAPIError(`Request failed: ${error.message}`);
        }
    }

    /**
     * Perform basic health check
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        return await this._request('/');
    }

    /**
     * Perform detailed health check
     * @returns {Promise<Object>} Detailed health status
     */
    async detailedHealthCheck() {
        return await this._request('/health');
    }

    /**
     * Predict drug interactions
     * @param {Drug[]} drugs - Array of Drug objects
     * @returns {Promise<InteractionPrediction[]>} Array of predictions
     */
    async predictInteractions(drugs) {
        if (!Array.isArray(drugs)) {
            throw new Error('Drugs must be an array');
        }

        if (drugs.length < 2) {
            throw new Error('At least 2 drugs are required for interaction prediction');
        }

        if (drugs.length > 10) {
            throw new Error('Maximum 10 drugs allowed per request');
        }

        const requestData = {
            drugs: drugs.map(drug => drug.toJSON ? drug.toJSON() : drug)
        };

        const response = await this._request('/predict-interactions', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });

        return response.predictions.map(pred => new InteractionPrediction(pred));
    }

    /**
     * Get API information
     * @returns {Promise<Object>} API information
     */
    async getApiInfo() {
        return await this._request('/api/info');
    }

    /**
     * Process multiple drug batches with rate limiting
     * @param {Drug[][]} drugBatches - Array of drug arrays
     * @param {number} delay - Delay between requests in milliseconds
     * @returns {Promise<InteractionPrediction[][]>} Array of prediction arrays
     */
    async predictInteractionsBatch(drugBatches, delay = 100) {
        const results = [];

        for (let i = 0; i < drugBatches.length; i++) {
            try {
                const predictions = await this.predictInteractions(drugBatches[i]);
                results.push(predictions);

                // Rate limiting delay
                if (i < drugBatches.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            } catch (error) {
                console.error(`Batch ${i + 1} failed:`, error.message);
                results.push([]);
            }
        }

        return results;
    }
}

// Example usage for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Drug,
        InteractionPrediction,
        DrugInteractionClient,
        DrugInteractionAPIError
    };

    // Example usage
    if (require.main === module) {
        (async () => {
            const client = new DrugInteractionClient('http://localhost:5000');

            try {
                // Check API health
                const health = await client.healthCheck();
                console.log(`API Status: ${health.status}`);

                // Create drug objects
                const warfarin = new Drug({
                    drug_name: "Warfarin",
                    pharmacodynamic_class: "Anticoagulant",
                    logp: 2.7,
                    therapeutic_index: "NTI",
                    transporter_interaction: "Substrate: P-gp",
                    plasma_protein_binding: 99.0,
                    metabolic_pathways: "Substrate: CYP2C9;CYP3A4"
                });

                const amiodarone = new Drug({
                    drug_name: "Amiodarone",
                    pharmacodynamic_class: "Antiarrhythmic",
                    logp: 7.6,
                    therapeutic_index: "NTI",
                    transporter_interaction: "Substrate: P-gp / Inhibitor: P-gp",
                    plasma_protein_binding: 96.0,
                    metabolic_pathways: "Substrate: CYP3A4 / Inhibitor: CYP2D6"
                });

                // Predict interactions
                const predictions = await client.predictInteractions([warfarin, amiodarone]);

                console.log('\nInteraction Analysis Results:');
                console.log('='.repeat(50));

                predictions.forEach(pred => {
                    console.log(`\n${pred.getDescription()}`);
                    console.log(`  Risk Level: ${pred.riskLevel}`);
                    console.log(`  Recommendation: ${pred.recommendation}`);
                });

            } catch (error) {
                console.error('Error:', error.message);
                if (error.details) {
                    console.error('Details:', error.details);
                }
            }
        })();
    }
}

// Browser usage example
if (typeof window !== 'undefined') {
    window.DrugInteractionAPI = {
        Drug,
        InteractionPrediction,
        DrugInteractionClient,
        DrugInteractionAPIError
    };
}
