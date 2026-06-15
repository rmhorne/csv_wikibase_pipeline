# Logic for the system
- This is a config driven engine. The engine is to be generaic; the config and the csv are the data that are operated on

## 1. Read in config file

Here sre secions.

### source object:
```
  "source": {
    "qid": "Q799",
    "label": "Milken Archive"
  },
```
THis establshes wher the data comes from. The QID is always valid as it is manually set from the wikibase. 



### Row object:
```
  "row": {
    "identity": {
      "fields": [
        "Title",
        "Composer"
      ],
      "separator": " | "
    },
    "label": {
      "field": "Title"
    },
    "on_create": [
      {
        "subject": {
          "source": "self",
          "as": "entity"
        },
        "predicate": "P1",
        "object": {
          "resolve": "expression",
          "as": "entity",
          "if_missing": "create"
        }
      }
    ]
  },

  ```
THis describes waht the row is. A row will always be an entity on the graoh. the actual system ID (sysID) is created by our ssytem.

the identiy block gives it its human readable idenity; we are specifiyig it comes from the fields of the record and it is a combination of data in the columns Title and omposer, separated by |.

Label is the wikibase label the iem weill get.

The on_crete_section is run IMMEDATELY follwonig the creation of the item  and the assigning of the sysID. this is built like our graoh 13objects. The on create block os omlyfired when this entity is created; thst way we are not doing multile statements that have to be fired later

subject: information on the subject of a tripple. 

    - Source: where the data. for that statment (subjct) is. Possible values are:
      - Self  = the VALUE of the field as the subject.  Unless specified otherwise, this is to be treated as an entitiy.
      - field = the VALUE of the COLUMN NAME, 
    - as: Says IF THIS AN ENITY OR A VALUE
      - entity = entiy
      - value = JUST THE VALUE OF T FIELD! DO NOT MAKE AN ENTITUY OF IT
    - 
predicateL THe predicate used to bind the subject and object. 


object: information on the subject of a tripple. same structures as graph in subject. THIs config shows some optionsal fields:
    Resolve: THis indicateds that this pat of sthe stament resilves to somehting that is in our graph. In this case it is teh enenty exporession (set by the as:)
    if_missing: Is the resolve entity can not be found, do someting. 
        create: = create it as an entity now' ensure the linkages declared by the fraoh object are made
        ignore: forget entitiy creation if the value is not resolved



### context object:

These are presistanct entites in positions that are established by the contedxt. THESE MUST BE CREATED.

example:

```
  "contexts": {
    "work": {
      "identity": {
        "fields": [
          "Title"
        ]
      },
        "if_missing": "row",
      "label": {
        "field": "Title"
      },
      "on_create": [
        {
          "subject": {
            "source": "self"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Work",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P70",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]

    },
      "manifestation": {
      "identity": {
        "fields": [
          "Spotify Album"
        ]
      },
        "if_missing": "row",
      "label": {
        "field": "Spotify Album"
      },
      "on_create": [
        {
          "subject": {
            "source": "self", "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "manifestation",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "self", "as":"entity"
          },
          "predicate": "P71",
          "object": {
            "source": "row",
            "as": "entity"
          }
        }
      ]
    }
  },

  ```

  In this example, we are creating a work entity and a manifestation entitiy, These are both named contexts.

  You will see that the start of each cntext is the dsame formart of the identity blocjk as for row.

  ```

      "work": {
      "identity": {
        "fields": [
          "Title"
        ]
      },
        "if_missing": "row",
      "label": {
        "field": "Title"
      },
      "on_create": [
        {
          "subject": {
            "source": "self"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Work",
            "as": "entity"
          }
        }
      ],


      ```

      the 
      ``` "if_missing": "row", ```
      
      option statses that if the work enttyu is missing or unable to be builtm then any statement or lookup loking for the work context is attached to row instead.

      The graph block has the same options as the on_create block. You can think of on_create 













This is a full example:
```
{
  "source": {
    "qid": "Q799",
    "label": "Milken Archive"
  },
  "row": {
    "identity": {
      "fields": [
        "Title",
        "Composer"
      ],
      "separator": " | "
    },
    "label": {
      "field": "Title"
    },
    "on_create": [
      {
        "subject": {
          "source": "self",
          "as": "entity"
        },
        "predicate": "P1",
        "object": {
          "resolve": "expression",
          "as": "entity",
          "if_missing": "create"
        }
      }
    ]
  },
  "contexts": {
    "work": {
      "identity": {
        "fields": [
          "Title"
        ]
      },
        "if_missing": "row",
      "label": {
        "field": "Title"
      },
      "on_create": [
        {
          "subject": {
            "source": "self"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Work",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P70",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]

    },
      "manifestation": {
      "identity": {
        "fields": [
          "Spotify Album"
        ]
      },
        "if_missing": "row",
      "label": {
        "field": "Spotify Album"
      },
      "on_create": [
        {
          "subject": {
            "source": "self", "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "manifestation",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "self", "as":"entity"
          },
          "predicate": "P71",
          "object": {
            "source": "row",
            "as": "entity"
          }
        }
      ]
    }
  },
  "fields": {
    "Composer": {
      "split": true,
      "delimiter": ";",
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Composer",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "self",
            "if_missing": "create"
          },
          "predicate": "P9",
          "object": {
            "source": "context",
            "context": "work"
          }
        }
      ]
    },
    "Duration (minutes)": {
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "manifestation"
          },
          "predicate": "P4",
          "object": {
            "source": "self",
            "as": "literal"
          }
        }
      ]
    },
    "Year (Known)": {
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P5",
          "object": {
            "source": "self",
            "as": "literal"
          },
          "certainty": "certain"
        }
      ]
    },
    "Year (Estimated)": {
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P5",
          "object": {
            "source": "self",
            "as": "literal"
          },
          "certainty": "uncertain"
        }
      ]
    },
    "Commissioning Institution (Name)": {
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Institution",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P12",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Primary Genre": {
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Primary Genre",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P13",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Instrumentation": {
      "split": true,
      "delimiter": ";",
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "instrumentation",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P14",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Form-General": {
      "split": true,
      "delimiter": "/",
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "musical form",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P15",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Form-Specific (was Tertiary Genre)": {
      "split": true,
      "delimiter": "/",
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "musical form",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P15",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Other": {
      "split": true,
      "delimiter": "/",
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "musical form",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "row"
          },
          "predicate": "P15",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Sacred": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Primary Genre",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P13",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Secular": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Primary Genre",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P13",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Ashkenazi": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Cultural Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P16",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Sephardi": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Cultural Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P16",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Israeli": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Cultural Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P16",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Mizrahi": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Cultural Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P16",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Musical": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Conceptual": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Textual": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Functional": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Sonic": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Social": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Judaic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P17",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Classical": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Klezmer": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Cantorial": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Folk": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Jazz": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Devotional-Solemn": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Popular": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Theatrical": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Stylistic Indicator",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work",
            "as": "entity"
          },
          "predicate": "P18",
          "object": {
            "source": "field",
            "as": "entity"
          }
        }
      ]
    },
    "Text Type": {
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Linguistic Indicator",
            "as": "entity"
          }
        },
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P19",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Text Source": {
      "on_create": [
        {
          "subject": {
            "source": "self",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Hebrew": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Yiddish": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "English": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "Ladino": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    },
    "German": {
      "condition": {
        "source": "self",
        "op": "equals",
        "value": "x",
        "normalize": true
      },
      "on_create": [
        {
          "subject": {
            "source": "field",
            "as": "entity"
          },
          "predicate": "P1",
          "object": {
            "resolve": "Text Source",
            "as": "entity"
          }
        }
      ],
      "graph": [
        {
          "subject": {
            "source": "context",
            "context": "work"
          },
          "predicate": "P20",
          "object": {
            "source": "self",
            "as": "entity"
          }
        }
      ]
    }
  }
}
```

