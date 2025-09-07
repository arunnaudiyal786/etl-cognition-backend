# Utility function to generate synthetic PowerCenter XML
def generate_synthetic_powercenter_xml() -> str:
    """Generate realistic PowerCenter XML for testing"""
    
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<POWERMART CREATION_DATE="12/15/2023 10:30:00" REPOSITORY_VERSION="9.6.1">
    <REPOSITORY NAME="SALES_DW_REPO" VERSION="1.0" CODEPAGE="UTF-8">
        <FOLDER NAME="SALES_ETL" GROUP="" OWNER="admin" SHARED="NOTSHARED">
            
            <!-- Source Definition -->
            <SOURCE BUSINESSNAME="" DATABASETYPE="Oracle" NAME="SRC_CUSTOMERS" 
                    OWNERNAME="SALES_DB" VERSIONNUMBER="1">
                <SOURCEFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="1" FIELDPROPERTY="0" FIELDTYPE="ELEMITEM" 
                           HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="50" 
                           NAME="CUSTOMER_ID" NULLABLE="NOTNULL" OCCURS="0" 
                           OFFSET="0" PRECISION="0" SCALE="0" USAGE_FLAGS=""/>
                <SOURCEFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="2" FIELDPROPERTY="0" FIELDTYPE="ELEMITEM" 
                           HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="100" 
                           NAME="CUSTOMER_NAME" NULLABLE="NULL" OCCURS="0" 
                           OFFSET="0" PRECISION="0" SCALE="0" USAGE_FLAGS=""/>
                <SOURCEFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="3" FIELDPROPERTY="0" FIELDTYPE="ELEMITEM" 
                           HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="10" 
                           NAME="CUSTOMER_STATUS" NULLABLE="NULL" OCCURS="0" 
                           OFFSET="0" PRECISION="0" SCALE="0" USAGE_FLAGS=""/>
            </SOURCE>
            
            <SOURCE BUSINESSNAME="" DATABASETYPE="Oracle" NAME="SRC_ORDERS" 
                    OWNERNAME="SALES_DB" VERSIONNUMBER="1">
                <SOURCEFIELD NAME="ORDER_ID" DATATYPE="decimal" LENGTH="10" PRECISION="0" SCALE="0"/>
                <SOURCEFIELD NAME="CUSTOMER_ID" DATATYPE="string" LENGTH="50" PRECISION="0" SCALE="0"/>
                <SOURCEFIELD NAME="ORDER_DATE" DATATYPE="date/time" LENGTH="19" PRECISION="0" SCALE="0"/>
                <SOURCEFIELD NAME="ORDER_AMOUNT" DATATYPE="decimal" LENGTH="15" PRECISION="2" SCALE="2"/>
            </SOURCE>
            
            <!-- Transformations -->
            <TRANSFORMATION DESCRIPTION="Filter active customers" NAME="FLT_ACTIVE_CUSTOMERS" 
                           OBJECTVERSION="1" TYPE="Filter" VERSIONNUMBER="1">
                <TRANSFORMFIELD DATATYPE="string" DEFAULTVALUE="" DESCRIPTION="" 
                              FIELDNUMBER="1" HIDDEN="NO" LENGTH="50" NAME="CUSTOMER_ID" 
                              PICTURETEXT="" PORTTYPE="INPUT" PRECISION="0" SCALE="0"/>
                <TRANSFORMFIELD DATATYPE="string" DEFAULTVALUE="" DESCRIPTION="" 
                              FIELDNUMBER="2" HIDDEN="NO" LENGTH="100" NAME="CUSTOMER_NAME" 
                              PICTURETEXT="" PORTTYPE="INPUT" PRECISION="0" SCALE="0"/>
                <TRANSFORMFIELD DATATYPE="string" DEFAULTVALUE="" DESCRIPTION="" 
                              FIELDNUMBER="3" HIDDEN="NO" LENGTH="10" NAME="CUSTOMER_STATUS" 
                              PICTURETEXT="" PORTTYPE="INPUT" PRECISION="0" SCALE="0"/>
                <TRANSFORMFIELD DATATYPE="string" DEFAULTVALUE="" DESCRIPTION="" 
                              FIELDNUMBER="1" HIDDEN="NO" LENGTH="50" NAME="CUSTOMER_ID" 
                              PICTURETEXT="" PORTTYPE="OUTPUT" PRECISION="0" SCALE="0"/>
                <TRANSFORMFIELD DATATYPE="string" DEFAULTVALUE="" DESCRIPTION="" 
                              FIELDNUMBER="2" HIDDEN="NO" LENGTH="100" NAME="CUSTOMER_NAME" 
                              PICTURETEXT="" PORTTYPE="OUTPUT" PRECISION="0" SCALE="0"/>
            </TRANSFORMATION>
            
            <TRANSFORMATION DESCRIPTION="Lookup customer details" NAME="LKP_CUSTOMER_DETAILS" 
                           OBJECTVERSION="1" TYPE="Lookup" VERSIONNUMBER="1">
                <TRANSFORMFIELD NAME="CUSTOMER_ID" PORTTYPE="INPUT" DATATYPE="string" LENGTH="50"/>
                <TRANSFORMFIELD NAME="CUSTOMER_NAME" PORTTYPE="OUTPUT" DATATYPE="string" LENGTH="100"/>
                <TRANSFORMFIELD NAME="CUSTOMER_TIER" PORTTYPE="OUTPUT" DATATYPE="string" LENGTH="20"/>
            </TRANSFORMATION>
            
            <TRANSFORMATION DESCRIPTION="Calculate order metrics" NAME="AGG_ORDER_SUMMARY" 
                           OBJECTVERSION="1" TYPE="Aggregator" VERSIONNUMBER="1">
                <TRANSFORMFIELD NAME="CUSTOMER_ID" PORTTYPE="INPUT" DATATYPE="string" LENGTH="50"/>
                <TRANSFORMFIELD NAME="ORDER_AMOUNT" PORTTYPE="INPUT" DATATYPE="decimal" LENGTH="15" PRECISION="2"/>
                <TRANSFORMFIELD NAME="CUSTOMER_ID" PORTTYPE="OUTPUT" DATATYPE="string" LENGTH="50"/>
                <TRANSFORMFIELD NAME="TOTAL_ORDERS" PORTTYPE="OUTPUT" DATATYPE="decimal" LENGTH="10"/>
                <TRANSFORMFIELD NAME="AVG_ORDER_VALUE" PORTTYPE="OUTPUT" DATATYPE="decimal" LENGTH="15" PRECISION="2"/>
            </TRANSFORMATION>
            
            <!-- Target Definition -->
            <TARGET BUSINESSNAME="" DATABASETYPE="Oracle" NAME="TGT_CUSTOMER_SUMMARY" 
                   OWNERNAME="DW_SCHEMA" VERSIONNUMBER="1">
                <TARGETFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="1" HIDDEN="NO" KEYTYPE="PRIMARY KEY" LENGTH="50" 
                           NAME="CUSTOMER_ID" NULLABLE="NOTNULL" PRECISION="0" SCALE="0"/>
                <TARGETFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="2" HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="100" 
                           NAME="CUSTOMER_NAME" NULLABLE="NULL" PRECISION="0" SCALE="0"/>
                <TARGETFIELD BUSINESSNAME="" DATATYPE="string" DESCRIPTION="" 
                           FIELDNUMBER="3" HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="20" 
                           NAME="CUSTOMER_TIER" NULLABLE="NULL" PRECISION="0" SCALE="0"/>
                <TARGETFIELD BUSINESSNAME="" DATATYPE="decimal" DESCRIPTION="" 
                           FIELDNUMBER="4" HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="10" 
                           NAME="TOTAL_ORDERS" NULLABLE="NULL" PRECISION="0" SCALE="0"/>
                <TARGETFIELD BUSINESSNAME="" DATATYPE="decimal" DESCRIPTION="" 
                           FIELDNUMBER="5" HIDDEN="NO" KEYTYPE="NOT A KEY" LENGTH="15" 
                           NAME="AVG_ORDER_VALUE" NULLABLE="NULL" PRECISION="2" SCALE="2"/>
            </TARGET>
            
            <!-- Mapping Definition -->
            <MAPPING DESCRIPTION="Customer summary ETL mapping" NAME="m_CUSTOMER_SUMMARY" 
                    OBJECTVERSION="1" VERSIONNUMBER="1" ISVALID="YES">
                <SHORTCUT FOLDERNAME="SALES_ETL" NAME="SRC_CUSTOMERS" OBJECTSUBTYPE="Source Definition" OBJECTTYPE="Source" REFERENCEDDBD="" REFERENCEDOBJECTNAME="SRC_CUSTOMERS" VERSIONNUMBER="1"/>
                <SHORTCUT FOLDERNAME="SALES_ETL" NAME="SRC_ORDERS" OBJECTSUBTYPE="Source Definition" OBJECTTYPE="Source" REFERENCEDDBD="" REFERENCEDOBJECTNAME="SRC_ORDERS" VERSIONNUMBER="1"/>
                <SHORTCUT FOLDERNAME="SALES_ETL" NAME="TGT_CUSTOMER_SUMMARY" OBJECTSUBTYPE="Target Definition" OBJECTTYPE="Target" REFERENCEDDBD="" REFERENCEDOBJECTNAME="TGT_CUSTOMER_SUMMARY" VERSIONNUMBER="1"/>
            </MAPPING>
            
        </FOLDER>
    </REPOSITORY>
</POWERMART>'''
    
    return xml_content
