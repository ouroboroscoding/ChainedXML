# ChainedXML Python Module

ChainedXML is a simple to use Python module that allows generation of XML documents in a way that is clear and straightforward. By using chained method calls an entire XML document can be made in one line of Python code.

## Introduction

Traditional XML classes/modules available often force you to make one element at a time and then add them to previous ones. This means creating various objects which serve no real purpose and might as well be deleted immediately after being used.

Not enjoying how terrible my code looked, and not wanting to use templates or manually generate XML that might end up being malformed, I opted to make my own wrapper for ElementTree which would allow my code to look as clean as the final XML document below.

```xml
<?xml version='1.0' encoding='utf-8'?>
<content>
   <header>
     <user>test</user>
     <pass>test</pass>
   </header>
   <body>
     <encrypt/>
     <subject>Testing</subject>
     <data><![CDATA[<b>This is my example content</b>]]></data>
   </body>
</content>
```

Using ChainedXML I can now write code like this:

```python
import ChainedXML

sXML  = ChainedXML.new('utf-8').                                    \
        add('content').                                             \
          add('header').                                            \
            add('user', text='test').                               \
            add('pass', text='pass').                               \
            root().                                                 \
          add('body').                                              \
            add('encrypt', current=False).                          \
            add('subject', text='Testing').                         \
            add('data', cdata='<b>This is my example content</b>'). \
        generate()
```

Doesn't that look better than most of the options out there?

## Methods

#### new(declaration, root)

- declaration *str* : If a declaration statement is needed, this must be set to the charset to use.
- root *str* : If we immediately want to create the root element we can pass it here, for example in the previous example ```add('content')``` could have been avoided if new had been called as ```new('utf-8', 'content')```

The new method is the way to start creating a new XML document. It has two arguments, neither of which are mandatory.

#### add(name, attr, text, cdata, current)

- name *str* : The name of the new tag. Must be set.
- attr *dict* : Optional list of attribute names and values. If not set the element will have no attributes.
- text *str* : Optional text to set inside the element. The string will be encoded to make sure it doesn't break the XML. When set the system assumes this is a leaf element and that the next added element will be a sibling and not a child. This behaviour can be overidden by setting the ```current``` arguments to ```True```
- cdata *str* : Optional CDATA to set inside the element. The string will not be touched or altered in any way. When set the system assumes this is a leaf element and that the next added element will be a sibling and not a child. This behaviour can be overidden by setting the ```current``` arguments to ```True```
- current *bool* : Optional argument that decides whether the new element will be a parent of the next elements, or a sibling itself. Defaults to True.

Add is a simple multiple purpose method that will allow you to create any sort of XML element. It relies on info passed to it to make judgement calls about what the next call to add will do. If text or cdata are filled the element is judged to be a final, or leaf, element. Meaning it will not have any children, other leaves or branches, and so should not be set as the parent of the next added element. If neither of these options are set the element is assumed to be the parent of proceeding elements. This default behaviour can be overidden via the ```current``` argument, which can be seen in use when creating the ```encrypt``` element in the example.

#### generate()

Generate contains no arguments and does exactly what you'd expect, it takes all the previous elements created and builds the XML which is then returned as a string.

#### root()

Root contains no arguments and sets the internal element pointer of the module to the root element. It is necessary for when you've hit the bottom of a set of branches and wish to start adding more children to the root. If there is currently no root element in the XML then root() will raise an exception.

#### up()

Up contains no arguments and is similar to root() in that it changes the internal element pointer of the module to the parent of the current element. It is useful in cases where you do not wish to start back at the root, but simply wish to bubble up one level so that you can create new children. If the current element has no parent element then up() will raise an exception.
