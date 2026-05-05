/**
 * ErrorBoundary Component - Catch errors in child components
 */

import React from 'react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({
            error,
            errorInfo,
        });
        console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={styles.container}>
                    <div style={styles.content}>
                        <h1>⚠️ Oops! Something went wrong</h1>
                        <p>The application encountered an error. Please try refreshing the page.</p>

                        {process.env.NODE_ENV === 'development' && (
                            <details style={styles.details}>
                                <summary>Error Details (Development Only)</summary>
                                <pre style={styles.pre}>
                                    {this.state.error && this.state.error.toString()}
                                    {this.state.errorInfo && this.state.errorInfo.componentStack}
                                </pre>
                            </details>
                        )}

                        <button
                            onClick={() => window.location.reload()}
                            style={styles.button}
                        >
                            Refresh Page
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

const styles = {
    container: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: '#f5f5f5',
        padding: '1rem',
    },
    content: {
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        maxWidth: '500px',
        textAlign: 'center',
    },
    details: {
        marginTop: '1rem',
        textAlign: 'left',
        background: '#f9f9f9',
        padding: '1rem',
        borderRadius: '4px',
        cursor: 'pointer',
    },
    pre: {
        overflow: 'auto',
        background: '#eee',
        padding: '0.5rem',
        borderRadius: '4px',
        fontSize: '0.85rem',
    },
    button: {
        marginTop: '1rem',
        padding: '0.75rem 1.5rem',
        background: '#2e7d32',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '1rem',
        fontWeight: '600',
    },
};

export default ErrorBoundary;
