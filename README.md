# PowerFlow AI Analyzer

A Python application that analyzes PowerCenter XML files and creates visual workflow diagrams using LangGraph.

## Features

- **PowerCenter XML Analysis**: Parses and extracts workflow information from PowerCenter XML files
- **LangGraph Workflow**: Uses LangGraph to create a structured workflow for data analysis
- **Graph Visualization**: Generates visual workflow diagrams as PNG files
- **AI-Powered Analysis**: Integrates with OpenAI for intelligent workflow analysis (optional)
- **Mock Mode**: Works without API keys for demonstration purposes

## Project Structure

```
Code/
├── app.py                 # Main application with LangGraph workflow
├── data.py               # Synthetic PowerCenter XML generator
├── requirements.txt      # Core dependencies
├── requirements-dev.txt  # Development dependencies
├── sample_powercenter.xml # Generated sample XML file
├── flow.png             # Generated workflow visualization
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

### Development Setup

For development with additional tools:

```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

```bash
python app.py
```

This will:
1. Generate a synthetic PowerCenter XML file
2. Parse and analyze the XML structure
3. Create a LangGraph workflow
4. Generate a visual diagram (`flow.png`)
5. Display analysis results

### With OpenAI Integration

To use AI-powered analysis:

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Run the application:
   ```bash
   python app.py
   ```

## Dependencies

### Core Dependencies

- **langgraph** (>=0.2.76): Workflow orchestration framework
- **langchain-core** (>=0.2.43): Core LangChain functionality
- **langchain-openai** (>=0.1.25): OpenAI integration
- **langchain** (>=0.2.17): LangChain framework
- **typing-extensions** (>=4.15.0): Enhanced typing support

### Optional Dependencies

- **pyppeteer** (>=0.2.6): For local Mermaid rendering
- **graphviz** (>=0.20.0): Alternative graph visualization
- **pandas** (>=2.0.0): Data analysis
- **matplotlib** (>=3.7.0): Plotting
- **fastapi** (>=0.100.0): Web API framework

## Workflow Structure

The LangGraph workflow consists of four main nodes:

1. **parse_xml**: Parses PowerCenter XML and extracts basic structure
2. **analyze_workflow**: Analyzes transformations and data flow logic
3. **map_dependencies**: Maps dependencies between sources, transformations, and targets
4. **summarize**: Generates human-readable workflow summary

## Output Files

- **sample_powercenter.xml**: Generated synthetic PowerCenter XML file
- **flow.png**: Visual workflow diagram showing the LangGraph structure

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for AI-powered analysis (optional)

### Model Configuration

The application uses GPT-4 by default but can be configured in the `PowerCenterWorkflowExtractor` class:

```python
extractor = PowerCenterWorkflowExtractor(llm_model="gpt-3.5-turbo")
```

## Error Handling

The application includes comprehensive error handling:
- Graceful fallback when OpenAI API is not available
- Mock responses for demonstration purposes
- Detailed error reporting in the output

## Development

### Code Style

The project uses:
- Black for code formatting
- Flake8 for linting
- MyPy for type checking

### Testing

Run tests with:
```bash
pytest
```

### Adding New Features

1. Add new nodes to the LangGraph workflow in `app.py`
2. Update the `WorkflowState` TypedDict if needed
3. Add corresponding node methods
4. Update dependencies in `requirements.txt` if needed

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: The application will work in mock mode without an API key
2. **Graph Visualization Error**: Ensure all dependencies are installed correctly
3. **XML Parsing Error**: Check that the XML file is valid PowerCenter format

### Getting Help

- Check the error messages in the console output
- Verify all dependencies are installed: `pip list`
- Test with the provided sample XML file

## License

This project is for educational and demonstration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Version History

- v1.0.0: Initial release with basic PowerCenter XML analysis and LangGraph workflow
