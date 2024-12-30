# GraphIOC

## Motivation

IOC is good, solved checking in things, envs like stage/prod good.

But it really hasn't it mdae it much easier to create infrastructure.

It is the ORM of infrastructure, easy to do simple things hard to do hard things.

It is easy in to create a db or a S# bucket, it is a hard to glue all the things together. What depends on what and what are the permissions.

Most of my time building infra strcuture is either figure out what needs to be created in what order or why something doesn't have permissions for something.

In Graph terms is it easy to define the nodes but difficult to define the edges. The infrastrucutre is useless without the edges.

Because of this it is very difficult to reuse IOC code. The node is a monolith with every attached to it so you can't just copy and paste because it is attached to everything else.

The other things is these tools tend to eat everything. They are the worst types of frameworks as when the break or behave in ways you don't like there is little to be done in the way to workaround them.






pip install --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz
			
			
			
Import -> Pydantic model (chat-gpt?)
