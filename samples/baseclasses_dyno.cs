using System;
using System.Collections.Generic;
using System.IO;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using Autodesk.Revit.Attributes;
using System.Windows.Input;
using System.Runtime.Remoting;
using System.Reflection;


namespace PyRevitBaseClasses {
    [Regeneration(RegenerationOption.Manual)]
    [Transaction(TransactionMode.Manual)]
    public abstract class PyRevitCommandDynamoBIM : IExternalCommand {
        public string baked_scriptSource = null;

        public PyRevitCommandDynamoBIM(string scriptSource) {
            baked_scriptSource = scriptSource;
        }

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements) {

            // 1: ---------------------------------------------------------------------------------------------------------------------------------------------
            #region Processing modifier keys
            // Processing modifier keys

            bool ALT = Keyboard.IsKeyDown(Key.LeftAlt) || Keyboard.IsKeyDown(Key.RightAlt);
            bool SHIFT = Keyboard.IsKeyDown(Key.LeftShift) || Keyboard.IsKeyDown(Key.RightShift);
            bool CTRL = Keyboard.IsKeyDown(Key.LeftCtrl) || Keyboard.IsKeyDown(Key.RightCtrl);
            bool WIN = Keyboard.IsKeyDown(Key.LWin) || Keyboard.IsKeyDown(Key.RWin);

            // If Alt clicking on button, open the script in explorer and return.
            if (ALT) {
                // combine the arguments together
                // it doesn't matter if there is a space after ','
                string argument = "/select, \"" + baked_scriptSource + "\"";

                System.Diagnostics.Process.Start("explorer.exe", argument);
                return Result.Succeeded;
            }
            #endregion

            // 2: ---------------------------------------------------------------------------------------------------------------------------------------------
            #region Execute and return results
            bool showDynamoGUI = CTRL || DetermineShowDynamoGUI();
            var journalData = new Dictionary<string, string>() {
                // Specifies the path to the Dynamo workspace to execute.
                { "dynPath", baked_scriptSource },

                // Specifies whether the Dynamo UI should be visible (set to false - Dynamo will run headless).
                { "dynShowUI", showDynamoGUI.ToString() },

                // If the journal file specifies automation mode
                // Dynamo will run on the main thread without the idle loop.
                { "dynAutomation",  "True" },

                // The journal file can specify if the Dynamo workspace opened
                //{ "dynForceManualRun",  "True" }

                // The journal file can specify if the Dynamo workspace opened from DynPathKey will be executed or not. 
                // If we are in automation mode the workspace will be executed regardless of this key.
                { "dynPathExecute",  "True" },

                // The journal file can specify if the existing UIless RevitDynamoModel
                // needs to be shutdown before performing any action.
                // per comments on https://github.com/eirannejad/pyRevit/issues/570
                // Setting this to True slows down Dynamo by a factor of 3
                { "dynModelShutDown",  "True" },

                // The journal file can specify the values of Dynamo nodes.
                //{ "dynModelNodesInfo",  "" }
                };

            //return new DynamoRevit().ExecuteCommand(new DynamoRevitCommandData() {
            //    JournalData = journalData,
            //    Application = commandData.Application
            //});

            try {
                // find the DynamoRevitApp from DynamoRevitDS.dll
                // this should be already loaded since Dynamo loads before pyRevit
                ObjectHandle dynRevitAppObjHandle = Activator.CreateInstance("DynamoRevitDS", "Dynamo.Applications.DynamoRevitApp");
                object dynRevitApp = dynRevitAppObjHandle.Unwrap();
                MethodInfo execDynamo = dynRevitApp.GetType().GetMethod("ExecuteDynamoCommand");

                // run the script
                return (Result)execDynamo.Invoke(dynRevitApp, new object[] { journalData, commandData.Application });
            }
            catch (FileNotFoundException) {
                // if failed in finding DynamoRevitDS.dll, assume no dynamo
                TaskDialog.Show("pyRevit", "Can not find dynamo installation or determine which Dynamo version to Run.\n\nRun Dynamo once to select the active version.");
                return Result.Failed;
            }
            #endregion
        }

        // NOTE: Dyanmo uses XML in older file versions and JSON in newer versions. This needs to support both if ever implemented
        private bool DetermineShowDynamoGUI() {
            return false;
            //    bool res = false;
            //    var xdoc = new XmlDocument();
            //    try {
            //        xdoc.Load(baked_scriptSource);
            //        XmlNodeList boolnode_list = xdoc.GetElementsByTagName("CoreNodeModels.Input.BoolSelector");
            //        foreach (XmlElement boolnode in boolnode_list) {
            //            string nnattr = boolnode.GetAttribute("nickname");
            //            if ("ShowDynamo" == nnattr) {
            //                Boolean.TryParse(boolnode.FirstChild.FirstChild.Value, out res);
            //                return res;
            //            }
            //        }
            //    }
            //    catch {
            //    }
            //    return res;
        }
    }
}
