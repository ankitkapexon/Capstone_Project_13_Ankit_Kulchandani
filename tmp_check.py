import importlib.util
print('appium', bool(importlib.util.find_spec('appium')))
print('selenium', bool(importlib.util.find_spec('selenium')))
print('appium_options', bool(importlib.util.find_spec('appium.options.android')))
