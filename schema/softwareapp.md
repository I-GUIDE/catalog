# Software Application

Software applications are programs designed for end-users to perform specific tasks. These applications are a subset of software and come in different types: desktop applications, mobile applications, and web applications. Examples include HEC-RAS software, Instagram, and the National Map Viewer. To classify a record as a software application, `"@type: "SoftwareApplication"` should be used in the json schema. Records classifed as `SoftwareApplication` should be described using the [core metadata](https://github.com/I-GUIDE/data-catalog/blob/main/schema/core.md), as well as the software application specific properties for the [Schema:SoftwareApplication](https://schema.org/SoftwareApplication) class. The following table outlines the required and optional properties selected from Schema.Org vocabulary to design the software application metadata schema. These properties are encoded as `1` or `1+` for **required** and `0,1` or `0+` for **optional** in the Cardinality column of the table below. 

|Property|Class|Expected Type|Cardinality|Description|
|---|---|---|---|---|
| [applicationCategory](#application-category) | SoftwareApplication | Text \| URL | 0,1 | Type of software application, e.g., research application, web application, desktop application, game application. |
| [applicationSubCategory](#application-sub-category) | SoftwareApplication | Text \| URL | 0+ | Subcategory of the application, e.g., subsurface flow modeling, predict, evaluate, train, collect. |
| [memoryRequirements](#memory-requirements) | Text | SoftwareApplication | 0,1 | Minimum memory requirements. |
| [processorRequirements](#processor-requirements) | Text | SoftwareApplication | 1+ | Processor architecture required to run the application (e.g. IA64). |
| [storageRequirements](#storage-requirements) | Text \| URL | SoftwareApplication | 0+ | Storage requirements (free space required). |
| [softwareRequirements](#software-requirements) | Text \| URL | SoftwareApplication | 1+ | Component dependency requirements for application. This includes runtime environments and shared libraries that are not included in the application distribution package, but required to run the application (examples: DirectX, Java or .NET runtime). Other example could be AWS or Local. |
| [operatingSystem](#operating-system) | Text | SoftwareApplication | 1+ | Operating systems supported (Windows 7, OS X 10.6, Android 1.6). |
| [supportingData](#supporting-data) | DataFeed | SoftwareApplication | 1+ | Supporting data for a SoftwareApplication. This can be used to catalog the inputs and outputs. |
| [softwareAddOn](#software-add-on) | SoftwareApplication | SoftwareApplication | 0+ | Additional content for a software application. |
| [featureList](#feature-list) | Text \| URL | SoftwareApplication | 1+ | Features or modules provided by this application (and possibly required by other applications). This can be used to list the outputs of the model. |
| [accessibilityAPI](#accessibility-api) | Text | CreativeWork | 1+ | Indicates that the resource is compatible with the referenced accessibility API. Values should be drawn from the [approved vocabulary](https://www.w3.org/community/reports/a11y-discov-vocab/CG-FINAL-vocabulary-20230718/#accessibilityAPI-vocabulary). |
| [conditionsOfAccess](#conditions-of-access) | Text | CreativeWork | 1+ | Conditions that affect the availability of, or method(s) of access to, an item. For example, if users need to create an account or join a specific group of community to use the application.  |
| [releaseNotes](#release-notes) | Text \| URL | SoftwareApplication | 1+ | Description of what changed in this version. |
| [softwareVersion](#software-version) | Text | SoftwareApplication | 0,1 | Version of the software instance. |
| [softwareHelp](#software-help) | DigitalDocument \| WebPage | SoftwareApplication | 1+ | Software application help. |


### Application Category

[applicationCategory](https://schema.org/applicationCategory) is used to specify the general type of a software application. It provides a high-level classification that helps users understand the primary function or purpose of the application. Types can include research application, web application, desktop application, game application, etc. 

A simple example is shown below.

``` json
{
  "": [
    "Hydrological Modeling Application",
    ""
  ]
}
```

### Application Sub-Category

[applicationSubCategory](https://schema.org/applicationSubCategory) provides additional detail about application category and helps users narrow down the type to its specific context.  

A simple example is shown below.

``` json
{
  "applicationSubCategory": [
    "Subsurface Flow Modeling",
    "Prediction of Subsurface Flow",
    "Time Series Anlaysis"
  ]
}
```

### Memory Requirements

[memoryRequirements](https://schema.org/memoryRequirements) specifies the minimum memory requirements.

A simple example is shown below.

``` json
{
  "memoryRequirements": "8 GB RAM"
}
```

### Processor Requirements

[processorRequirements](https://schema.org/processorRequirements) is used to describe information about the recommended processor specifications needed for a software application to function properly.

A simple example is shown below.

``` json
{
  "processorRequirements": [
    "4 CPU cores (2.5 GHz or faster)", 
    "2 GPU cores (NVIDIA or AMD)"]
}
```

### Storage Requirements

[storageRequirements](https://schema.org/storageRequirements) used to describe the amount of disk space that needs to be available to install and run a software application.

A simple example is shown below.

``` json
{
  "storageRequirements": "100 MB available storage"
}
```

### Software Requirements

[softwareRequirements](https://schema.org/softwareRequirements) is used to specify the dependency requirements to install and run a software application. These requirements can include runtime environments, shared libraries, and network specifications that are not included in the application distribution package, but are required for the application to function correctly. Examples are DirectX, Java or .NET runtime, AWS, etc. 

A simple representation is shown below. 

``` json
{
  "softwareRequirements": [
    "Java 8 or later",
    "Internet connection",
    "NVIDIA CUDA 10.1 or later",
    "OpenCL 2.0 compatible"
  ]
}
```

### Operating System

[operatingSystem](https://schema.org/operatingSystem) should identify the supported operating system(s) for the software application. 

A simple example is shown below.

``` json
{
  "operatingSystem": [
    "Windows 10",
    "Linux"
  ]
}
```

### Supporting Data

[supportingData](https://schema.org/supportingData) is used to identify and link to additional datasets that support or are used by a software application.

For example, a GIS software application might use the following supporting data to reference land cover or demographic data as base maps.

``` json
{
  "supportingData": [
    {
      "@type": "Dataset",
      "name": "Global Land Cover Dataset",
      "url": "https://example.com/global-land-cover"
    },
    {
      "@type": "Dataset",
      "name": "Census Data",
      "url": "https://example.com/census-data"
    }
  ]
}
```

### Software Add-On

[softwareAddOn](https://schema.org/softwareAddOn) provides information about additional content for a software application.

A simple example is shown below. This indicates that `TimeManager`, a capability that allows users to animate and explore time-based data, is an add-on software to the QGIS software application.

``` json
{
  "softwareAddOn": {
    "@type": "SoftwareApplication",
    "name": "TimeManager",
    "url": "https://plugins.qgis.org/plugins/timemanager/"
  }
}
```

### Feature List

[featureList](https://schema.org/featureList) is a list of modules or features that a software application provides. 

A simple example is shown below.

``` json
{
  "featureList": ["Data Disovery", "Data Publication", "Cloud Computing"]
}
```

### Accessibility API

[accessibilityAPI](https://schema.org/accessibilityAPI) indicates the accessibility API that a web application supports. In other words, it helps describe how the software interacts with assistive technologies to make it accessible to people with disabilities. The `accessibilityAPI` property could include several values, depending on the specific APIs supported by the web application. Common values might include ARIA (Accessible Rich Internet Applications) and WAI-ARIA (Web Accessibility Initiative – Accessible Rich Internet Applications). 

A simple example is shown below.

``` json
{
  "accessibilityAPI": ["ARIA", "WAI-ARIA"]
}
```

### Conditions Of Access

[conditionsOfAccess](https://schema.org/) is a description of conditions that affect the availability of, or method(s) of access to, an item. For example, if users need to create an account or join a specific group of community to use the application.

A simple example is shown below.

``` json
{
  "conditionsOfAccess": "Users need to create a free account to be able to use HydroShare for sharing their scientific water data."
}
```

### Release Notes

[releaseNotes](https://schema.org/releaseNotes) describes what changed in a specific version of the software application.

A simple example is shown below.

``` json
{
  "releaseNotes": "https://github.com/hydroshare/hydroshare/releases"
}
```

### Software Version

[softwareVersion](https://schema.org/softwareVersion) property indicates the version of the software instance.

A simple example is shown below.

``` json
{
  "softwareVersion": "Release 2.15.4"
}
```

### Software Help

[softwareHelp](https://schema.org/softwareHelp) can be used to identify link(s) to the software application help documentation, including but not limited to user guide, user manual, about page, etc. 

The following shows examples of `DigitalDocument` and `WebPage` classes (data types) that are used to describe `softwareHelp`.

``` json
{
  "softwareHelp": [{
    "@type": "DigitalDocument",
    "name": "HEC-RAS User's Manual",
    "description": "This user manual explains how to perform one-dimensional steady flow, one and twodimensional unsteady flow calculations, sediment transport/mobile bed computations, and water temperature/water quality modeling.",
    "archivedAt": "https://www.hec.usace.army.mil/software/hec-ras/documentation/HEC-RAS%20User's%20Manual-v6.4.1.pdf"
  }]
}

{
  "softwareHelp": [
    {
        "@type": "WebPage",
        "name": "HydroShare ",
        "description": "This web page includes links to learn how to begin sharing and collaborating using the HydroShare system.",
        "archivedAt": "https://help.hydroshare.org/"
    },
    {
        "@type": "WebPage",
        "name": "HydroShare Architecture",
        "description": "This web page describes the HydroShare architecture.",
        "archivedAt": "https://help.hydroshare.org/about-hydroshare/hydroshare-architecture/"
    }
  ]
}
```

