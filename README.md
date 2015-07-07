# bibframe-socket Socket Service
This small socket server wraps the Library of Congress'
[marc2bibframe][marc2bibframe].

## Installing
Use git to clone the repository and then follow these directions to load 
[marc2bibframe][marc2bibframe] as a submodule. 

    $ git clone https://github.com/jermnelson/bibframe-socket.git
    $ cd bibframe-socket
    $ git submodule init
    $ git submodule update

After you have to create a server.json in the bibframe-socket directory 
that has the following dictionary (set the base_uri to what you want 
it be for the XQuery transformations and the change the saxon_xqy 
property to the full file-path where you are running the project).

{
  "base_uri": "http://prospector.coalliance.org/",
  "saxon_xqy": "E:\\bibframe-socket\\marc2bibframe\\xbin\\saxon.xqy"
}

## Running
To run bibframe-socket on local host on port 8089:

$ jython server.py 0.0.0.0 8089

You can then send raw MARC21 XML to socket 8089 and BIBFRAME RDF XML
will be returned. See this [gist](https://gist.github.com/jermnelson/872c32d689bfbd6c0fec)
on the **xquery_chain** function that uses the bibframe-socket server.

## As Tomcat webapp

Creating a WAR file:

`/opt/jdk/bin/jar cvf bfsocket.war .`

[marc2bibframe]: https://github.com/lcnetdev/marc2bibframe/
