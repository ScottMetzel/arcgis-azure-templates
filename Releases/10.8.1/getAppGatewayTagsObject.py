#!/usr/bin/env python

"""
   Copyright 2020 Esri
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.​
"""


import sys, json, argparse

def _arg_parser():
    parser = argparse.ArgumentParser(description="Upload patches to share")
    parser.add_argument("--dt", default=None, help="Enterprise Deployment Type")
    parser.add_argument("--agtf", default=None, help="App Gateway Tags Temp File Name")
    parser.add_argument("--tmpf", default=None, help="Template Parameters File Name")
    return parser.parse_args()

def _main(args):
    params = json.load(open(args.tmpf))
    isBaseDeployment = False if 'federateSite' in params['parameters'].keys() else True
    if args.dt == "new":
        agTags = {
            "arcgis-deployment-id" : "[variables('deploymentId')]",
            "arcgis-deployment-version" : "[parameters('arcgisDeploymentVersion')]",
            "arcgis-deployment-info" : "[concat(parameters('deploymentPrefix'),'@',parameters('existingVirtualNetworkName'),'@',parameters('virtualNetworkResourceGroupName'),'@',parameters('subnetName'),'@',parameters('serverContext'),',',parameters('portalContext'),'@',parameters('deploymentTimestamp'))]" if isBaseDeployment else "[concat(parameters('deploymentPrefix'),'@',parameters('existingVirtualNetworkName'),'@',parameters('virtualNetworkResourceGroupName'),'@',parameters('subnetName'),'@',parameters('serverContext'),',',parameters('geoeventServerContext'),'@',parameters('deploymentTimestamp'))]",
            "arcgis-deployment-domain": "[parameters('externalDnsHostName')]",
            "arcgis-deployment-privateip-info": "[if(parameters('usesPrivateIP'),concat(parameters('appGatewayPrivateIP'),'@',parameters('appGatewayPrivateIPSubnet'),'@',parameters('existingVirtualNetworkName'),'@',parameters('virtualNetworkResourceGroupName'),'@',parameters('location')),'')]",
            "arcgis-deployment-publicip-info": "[if(not(parameters('usesPrivateIP')),concat(variables('publicIPAddressResourceName'),'@',variables('publicIPAddressResourceGroupName'),'@',parameters('location'),'@',parameters('dnsPrefixForPublicIpAddress'),'@',reference(resourceId(variables('publicIPAddressResourceGroupName'),'Microsoft.Network/publicIPAddresses/', variables('publicIPAddressResourceName')),'2020-04-01').ipAddress),'')]",
            "arcgis-deployment-server-role" : "HostingServer" if isBaseDeployment else "[parameters('serverRole')]",
            "arcgis-deployment-datastore-types" : "[parameters('dataStoreTypes')]" if isBaseDeployment else "",
            "arcgis-deployment-rdp-endpoint" : "[if(equals(string(parameters('enableRDPAccess')),'True'),concat(reference(concat('fetchIpAddress-',deployment().name),'2018-05-01').outputs.ipFqdn.value,':3389'),'')]",
            "arcgis-deployment-cloud-stg" : "[variables('cloudStorageOption')[string(parameters('useCloudStorage'))]]",
            "arcgis-deployment-oms-workspace" : "[variables('omsWorkspace')[string(not(empty(parameters('omsWorkspaceName'))))]]",
            "arcgis-deployment-autovmshutdown" : "[concat(string(parameters('enableAutoShutDown')),',',parameters('autoShutDownTime'))]"
        }
        print(json.dumps(agTags, indent=4))
    else:
        agTags = json.load(open(args.agtf))    
        params['parameters']['serverRole']
        if not isBaseDeployment:
            matches = [val for key, val in agTags.iteritems() if key.startswith('FS@'+params['parameters']['serverRole']+'@'+params['parameters']['serverContext']+','+ params['parameters']['geoeventServerContext']+'@')]
            if not matches:
                tagKey = "[concat('FS@',parameters('serverRole'),'@',parameters('serverContext'),',',parameters('geoeventServerContext'),'@',variables('deploymentId'),'@',parameters('deploymentTimestamp'))]" 
                agTags[tagKey] = "[concat(resourceGroup().name,',',resourceGroup().location,'@',parameters('deploymentPrefix'),'@',parameters('cloudStorageAccountResourceGroupName'),',',parameters('cloudStorageAccountName'),',',string(parameters('useAzureFiles')),'@',variables('omsWorkspace')[string(not(empty(parameters('omsWorkspaceName'))))],'@',string(parameters('enableAutoShutDown')),',',string(parameters('autoShutDownTime')))]"

            if not [val for key, val in agTags.iteritems() if key.startswith("arcgis-deployment-datastore-types")]:
                agTags["arcgis-deployment-datastore-types"] = "[parameters('dataStoreTypes')]" if isBaseDeployment else ""
        print(json.dumps(agTags, indent=4))
if __name__ == "__main__":
    sys.exit(_main(_arg_parser()))