CSRCS		= $(wildcard src/*.c)
CNAMES	= $(CSRCS:src/%.c=%)

COBJS		= $(CNAMES:%=build/obj/%.o)
CPROGS	= $(CNAMES:%=build/bin/%)

PROGS 	= $(CPROGS)

CNAME		= $(basename $(@F))
CSRC		= $(CNAME:%=src/%.c)
COBJ		= $(CNAME:%=build/obj/%.o)


MKDIR		= @mkdir -p $(@D)
IDIR		= /proj/contest

all: $(PROGS)

install: all
	@mkdir -p $(IDIR)/bin
	@mkdir -p $(IDIR)/grader/bin
	@mkdir -p $(IDIR)/grader/data
	@mkdir -p $(IDIR)/grader/txt
	@mkdir -p $(IDIR)/db
	cp build/bin/* $(IDIR)/bin
	cp py/* $(IDIR)/grader/bin
	cp data/* $(IDIR)/grader/data
	cp txt/* $(IDIR)/grader/txt
	bin/sql.py <db/tests.sql
	bin/sql.py <db/results.sql
	bin/sql.py <db/checkouts.sql
	chown -R contest:contest $(IDIR)
	chmod 4511 $(IDIR)/bin/*
	chmod 500 $(IDIR)/grader/
	chmod 500 $(IDIR)/grader/bin/*
	chmod 400 $(IDIR)/grader/data/*
	chmod 400 $(IDIR)/grader/txt/*

clean:
	rm -rf build

.SECONDARY:
.SECONDEXPANSION:

$(COBJS): $$(CSRC)
	$(MKDIR)
	gcc -pedantic -c -o $@ $<

$(CPROGS): $$(COBJ)
	$(MKDIR)
	gcc -o $@ $<
