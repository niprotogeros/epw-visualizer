
# Examples Directory

This directory is intended for example EPW files and usage demonstrations.

## Getting EPW Files

EPW (EnergyPlus Weather) files contain hourly weather data for specific locations. You can download them from several sources:

### Official Sources
- **[Ladybug Tools Epwmap](https://www.ladybug.tools/epwmap/)** - An interactive web tool to easily locate and download free .epw files from around the world from multiple sourses
- **[EnergyPlus Weather Data](https://energyplus.net/weather)** - The primary source with global coverage
- **[Climate.OneBuilding.Org](https://climate.onebuilding.org/)** - Comprehensive weather data repository
- **[NREL](https://sam.nrel.gov/weather-data.html)** - National Renewable Energy Laboratory data

### Future Weather Scenarios
- **[Future Weather Generator](https://future-weather-generator.adai.pt/)** - A free app for researchers and building design professionals. 
- It morphs present-day hourly EPW files used in dynamic simulation to match climate change scenarios and the urban heat island effect.

### Popular Locations to Try
- Major cities (New York, London, Tokyo, Sydney)
- Extreme climates (Phoenix for hot/dry, Miami for hot/humid, Anchorage for cold)
- Your local area for personal interest

## Usage Examples

### Basic Usage
```bash
python epw_visualizer.py path/to/weather_file.epw
```

### Example Workflow
1. Download an EPW file from one of the sources above
2. Place it in this `examples/` directory
3. Run the visualizer:
   ```bash
   python epw_visualizer.py examples/your_downloaded_file.epw
   ```

## File Naming Convention

When adding example files, consider using descriptive names:
- `USA_NY_New.York.JFK.Intl.AP.744860_TMY3.epw`
- `GBR_London.Heathrow.037720_IWEC.epw`
- `AUS_Sydney.947670_IWEC.epw`

## Educational Use Cases

This tool is particularly useful for:
- **Climate Studies**: Compare weather patterns between different locations
- **Building Design**: Understand local climate conditions for architecture
- **Renewable Energy**: Analyze solar and wind potential
- **Agriculture**: Study growing season conditions
- **General Education**: Learn about global climate patterns

## Contributing Examples

If you create interesting visualizations or find particularly educational EPW files:
1. Consider sharing them with the community
2. Add documentation about what makes them interesting
3. Follow the contribution guidelines in [CONTRIBUTING.md](../CONTRIBUTING.md)

## Note on File Sizes

EPW files are typically 1-3 MB each. Due to repository size considerations, we don't include actual EPW files in this repository. Users should download them from the official sources listed above.
