# References

These are the main external references this scaffold is based on:

- Autodesk: Creating a Script or Add-In
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WritingDebugging_UM.htm
- Autodesk: User-Interface Customization
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/UserInterface_UM.htm
- Autodesk: Fusion Commands
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Commands_UM.htm
- Autodesk: ExportManager.createC3MFExportOptions
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_createC3MFExportOptions.htm
- Autodesk: ExportManager.execute
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/ExportManager_execute.htm

## Important Constraint

According to Autodesk API guidance and community answers, existing built-in Fusion commands are not designed to be extended in place. The project therefore creates its own custom command instead of trying to patch the native `3D Print` dialog.
