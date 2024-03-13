# Plugin
A plugin is a programmable API which enables define customizable server components.
Plugins can be loaded at server startup, or reloaded and unloaded at runtime without restarting the server.

## Type of Plugins

We define four types of plugins currently, which includes:

- Audit: audit plugins provide the auditing functionality, we default implement FileAuditPlugin which persist audit
  log to file
- Procedure: procedure plugins provide procedures;
- Function: function plugins provide functions;
- Storage: not defined yet;

## Integrated with other component

- Plugin
    - Compiled to dynamic library at compile time;
    - Loaded into the database kernel by ModelManager during runtime;
- ModuleManager
    - Responsible for dynamic library management;
    - Plugin developers mostly do not need to know the internal implementation of module management,
      the only thing they need how to register a Plugin into the system; (use the
      nebula_module_load/nebula_module_unload function)
- User of Plugins
    - Functions/Procedures etc. implemented by Plugins are provided as Function/Procedure instance in Holder to other
      component of the system, they are the users of plugins.

```
                    ┌──────────┐    compiled to       ┌───────┐                             
                    │  Plugin  │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─▶│dynamic│                             
                    └──────────┘                      │library│                             
                          ▲                       │   └───────┘                             
       ┌───────────┬──────┴────┬───────────┐              │ load                            
       │           │           │           │      │       ▼        ┌─────────┐              
 ┌──────────┐┌──────────┐┌──────────┐┌──────────┐    ┌────────┐    │Function │              
 │  Audit   ││Procedure ││ Function ││ Storage  │ │  │ Module │    ├─────────┤              
 │  Plugin  ││  Plugin  ││  Plugin  ││  Plugin  │    └────────┘    │Procedure│              
 └─────▲────┘└─────▲────┘└──────────┘└──────────┘ │       ▲        ├─────────┤              
       │           │                                      │        │  Audit  │              
┌──────┴────┐┌─────┴─────┐                        │   lifecycle    ├─────────┤  ┌──────────┐
│   File    ││   Dbmc    │                            management   │ Storage │  │Planner   │
│   Audit   ││ Procedure │                        │  ┌─────────┐   └─────────┘  │/Optimizer│
│  Plugin   ││  Plugin   │                           │ Module  ├───────────────▶│/Runtime  │
└───────────┘└───────────┘                        │  │ Manager │    provides    │/etc...   │
                                                     └─────────┘                └──────────┘
```
