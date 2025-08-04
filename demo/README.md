# PyMevol Plus Demo Notebooks

Welcome to the PyMevol Plus demonstration notebooks! These interactive Jupyter notebooks will guide you through all aspects of using PyMevol Plus for PyPI package API evolution analysis.

## 📚 Notebook Overview

### 1. 🎓 [Basic API Usage](01_basic_api_usage.ipynb)
**Perfect for beginners** - Learn the core concepts and data structures.

**What you'll master:**
- 🏗️ **Core Models**: `APIElement`, `APIType`, `VersionInfo`, `APIChange`, `AnalysisResult`
- 🔍 **Data Inspection**: Understanding API signatures, types, and metadata
- 📊 **Analysis Methods**: Filtering, querying, and extracting insights
- 💾 **Serialization**: Saving and loading analysis results
- 📈 **Lifecycle Analysis**: Tracking stability, churn, and evolution patterns

**Time to complete:** ~30-45 minutes

### 2. 🔬 [Real Package Analysis](02_real_package_analysis.ipynb) 
**Hands-on with real data** - Analyze actual PyPI packages step by step.

**What you'll learn:**
- 📦 **Package Selection**: Choosing versions and analysis strategies  
- ⚡ **Performance**: Optimizing analysis for large packages
- 🌐 **PyPI Integration**: Fetching and processing real package data
- 📋 **Results Interpretation**: Understanding real-world API evolution patterns
- 🎯 **Targeted Analysis**: Focusing on specific modules, API types, or time periods

**Target packages included:** `click`, `requests`, `flask`, `numpy`, `pandas`, and more!
**Time to complete:** ~45-60 minutes

### 3. 🎨 [Visualization Examples](03_visualization_examples.ipynb)
**Make your data beautiful** - Create compelling charts and interactive dashboards.

**Visualization types covered:**
- 📈 **Timeline Charts**: API lifecycle visualization over time
- 📊 **Distribution Plots**: API type breakdowns and change patterns  
- 🔄 **Evolution Matrices**: Version-to-version change heatmaps
- 📉 **Trend Analysis**: Growth, stability, and churn metrics
- 🎪 **Interactive Dashboards**: Multi-panel exploration tools

**Libraries used:** Plotly, Matplotlib, Seaborn, Pandas
**Time to complete:** ~60-90 minutes

### 4. 🚀 [Advanced Features](04_advanced_features.ipynb) 
**Power user techniques** - Advanced analysis and customization.

**Advanced topics:**
- 🔍 **Custom Filters**: Building complex API selection criteria
- 📊 **Comparative Analysis**: Multi-package evolution studies  
- 🏗️ **Plugin System**: Extending PyMevol Plus with custom analyzers
- ⚙️ **Configuration**: Fine-tuning analysis parameters
- 🎯 **Specialized Reports**: Custom output formats and templates

**Time to complete:** ~75-120 minutes

### 5. 💻 [CLI Usage Guide](05_cli_usage.ipynb)
**Command-line mastery** - Batch processing and automation.

**CLI workflows:**
- 🔄 **Batch Analysis**: Processing multiple packages automatically  
- 📊 **Report Generation**: Creating HTML, Markdown, and CSV reports
- ⚡ **Performance Tuning**: Optimizing for large-scale analysis
- 🔧 **Integration**: Using PyMevol Plus in CI/CD pipelines
- 📋 **Scripting**: Automating common analysis tasks

**Time to complete:** ~45-60 minutes

## 🚀 Getting Started

### Prerequisites
```bash
# Ensure you have PyMevol Plus installed
pip install -e /path/to/pymevol-plus

# Install optional visualization dependencies
pip install plotly matplotlib seaborn jupyter tqdm
```

### Quick Start
1. **Launch Jupyter**: `jupyter notebook` or `jupyter lab`
2. **Start with Basics**: Open `01_basic_api_usage.ipynb` 
3. **Follow the Flow**: Work through notebooks in order
4. **Experiment**: Try different packages and parameters!

### Environment Setup
```python
# Verify your installation
import pymevol
print(f"PyMevol Plus version: {pymevol.__version__}")

# Test with a quick analysis
from pymevol import PackageAnalyzer
analyzer = PackageAnalyzer()
print("✅ Ready to analyze!")
```

## 📖 Learning Path

### 🎯 For Complete Beginners
1. Start with `01_basic_api_usage.ipynb`
2. Try `02_real_package_analysis.ipynb` with a simple package like `click`
3. Explore `03_visualization_examples.ipynb` 
4. Graduate to advanced topics as needed

### 🔬 For Researchers
1. Review `01_basic_api_usage.ipynb` quickly
2. Deep dive into `02_real_package_analysis.ipynb`
3. Focus on `04_advanced_features.ipynb` for comparative studies
4. Use `05_cli_usage.ipynb` for large-scale automation

### 🏗️ For Developers/Maintainers  
1. Skim `01_basic_api_usage.ipynb` for reference
2. Focus on `02_real_package_analysis.ipynb` for dependency analysis
3. Use `03_visualization_examples.ipynb` for reports to stakeholders
4. Master `05_cli_usage.ipynb` for CI/CD integration

## 💡 Tips for Success

### 🎯 **Start Small**
- Begin with packages that have ~5-10 versions
- Use the sampling strategies in notebook 2
- Focus on recent versions first

### 📊 **Understand Your Data**
- Always inspect the summary before diving deep
- Pay attention to breaking changes
- Look for patterns in module organization

### 🔧 **Performance Matters**
- Large packages (like TensorFlow) can take hours to analyze
- Use version sampling for initial exploration
- Cache results using JSON serialization

### 🎨 **Customize Visualizations**
- Modify colors and layouts to match your reports
- Export plots as PNG/SVG for presentations
- Combine multiple charts for comprehensive dashboards

### 🤝 **Share Your Results**
- Export analysis results as JSON for collaboration
- Generate HTML reports for stakeholders
- Use GitHub integration for tracking dependency evolution

## 🛠️ Troubleshooting

### Common Issues

**ImportError: No module named 'pymevol'**
```bash
# Install PyMevol Plus in development mode
pip install -e /path/to/pymevol-plus
```

**Network timeouts during package fetching**
```python  
# Increase timeout in fetcher
fetcher = PyPIFetcher(timeout=300)  # 5 minutes
```

**Memory issues with large packages**
```python
# Use version sampling
versions = select_analysis_versions(all_versions, strategy=\"sample\", max_versions=5)
```

**Visualization not displaying**
```python
# Enable Plotly offline mode
import plotly.offline as pyo
pyo.init_notebook_mode(connected=True)
```

### Getting Help

- 📖 **Documentation**: Check the `docs/` folder
- 💡 **Examples**: Browse the `examples/` directory  
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Community**: Join discussions for tips and tricks

## 🎉 What's Next?

After completing these notebooks, you'll be ready to:

- 🔍 **Analyze Any Package**: Understand API evolution patterns in your dependencies
- 📊 **Create Reports**: Generate compelling visualizations for stakeholders  
- 🏗️ **Make Informed Decisions**: Choose stable APIs and plan for breaking changes
- 🚀 **Contribute**: Help improve PyMevol Plus with feedback and contributions

## 📝 Feedback

We'd love to hear about your experience! Please:

- ⭐ Star the repository if these notebooks helped you
- 🐛 Report any issues or unclear sections
- 💡 Suggest improvements or additional examples
- 🤝 Share your interesting findings with the community

Happy analyzing! 🚀📊✨

---

*Last updated: 2024 | PyMevol Plus Demo Notebooks*
