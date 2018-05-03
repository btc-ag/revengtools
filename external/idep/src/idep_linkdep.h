// idep_linkdep.h
#ifndef INCLUDED_IDEP_LINKDEP
#define INCLUDED_IDEP_LINKDEP

// This wrapper component defines 8 fully insulated classes:
//          idep_LinkDep: environment for analyzing link dependencies
//        idep_AliasIter: iterate over specified alias pairs
//      idep_UnaliasIter: iterate over specified unaliased directories
//        idep_CycleIter: iterate over cycles in the system
//       idep_MemberIter: iterate over members within a given cycle
//        idep_LevelIter: iterate over levels in the system
//    idep_ComponentIter: iterate over components on a given level
//   idep_DependencyIter: iterate over dependencies for a given component

#include <iosfwd>

class idep_AliasIter;
class idep_UnaliasIter;
class idep_CycleIter;
class idep_MemberIter;
class idep_LevelIter;
class idep_ComponentIter;
class idep_DependencyIter;

class idep_LinkDep_i;
class idep_LinkDep {
    idep_LinkDep_i *d_this;

    friend class idep_AliasIter;
    friend class idep_UnaliasIter;
    friend class idep_CycleIter;
    friend class idep_MemberIter;
    friend class idep_LevelIter;
    friend class idep_ComponentIter;
    friend class idep_DependencyIter;

  private:
    idep_LinkDep(const idep_LinkDep&);                  // not implemented
    idep_LinkDep& operator=(const idep_LinkDep&);       // not implemented

  public:
    // CREATORS
    idep_LinkDep();
    ~idep_LinkDep();

    // MANIPULATORS
    void addDependencyFile(const char *fileName);
        // Add a file containing dependencies to be parsed.  Parsing errors
        // will be reported during the calculation phase.  Note that the
        // empty string ("") is interpreted to mean <stdin>.

    const char *addAlias(const char *aliasName, const char *componentName);
        // Add an alias/component name pair to the set of aliases.  This
        // function returns 0 on success or a character string containing
        // a previously corresponding component name for this alias that is
        // not identical to the once specified here.

    int readAliases(std::ostream& err, const char *file);
        // Read a list of component aliases from the specified file.  Each
        // contiguous sequence of non-whitespace characters represents a name.
        // Names are also arranged into sequences.  The first name in a name
        // sequence represents the actual component name.  Names that follow
        // on the same line (horizontal sequence) or subsequent lines
        // (vertical sequence) are interpreted as aliases for that component
        // name.  A horizontal sequence is terminated by a newline ('\n')
        // unless preceded by a backslash ('\\').  A vertical sequence is
        // terminated by a blank line.  This function quietly returns 0 on
        // success.  If the specified file is not readable, this function
        // quietly returns -1.  If an alias that is inconsistent with a
        // previously specified alias is encountered, the conflicting aliases
        // are identified to the err stream.  After parsing is complete, the
        // number of offending aliases is returned as the value of this
        // function.

    void addUnaliasDirectory(const char *dirName);
        // Add a directory _not_ to be treated as a single unit by default.
        // This function has no effect if the directory has already been
        // specified.

    int readUnaliasDirectories(const char *file);
        // Add a list of unalias directories read from the specified file.
        // This function assumes that each contiguous sequence of
        // non-whitespace characters represents a directory to be added.
        // This function returns 0 unless the specified file is unreadable
        // or contains non-ascii characters.

    int calculate(std::ostream& err, int canonicalFlag = 1, int suffixFlag = 0);
        // Calculate link-time component dependencies.  This function returns
        // 0 on success, non-zero on error.  If an io-error occurs, the result
        // will be negative, and this object will be left in an invalid state.
        // Otherwise the number of components involved in cyclic dependencies
        // will be returned.  Specific errors will be reported to the indicated
        // output stream stream (err).  A non-zero canocialFlag argument
        // request a canonical representation of the dependencies -- i.e.,
        // containing no redundant, transitive edges.  Overriding this default
        // behavior causes the complete (transitive) graph to remain.  Also by
        // default, all file suffixes are removed.  Passing a non-zero value
        // for the optional suffixFlag argument causes individual component
        // files to be treated as separate physical entities.

    // ACCESSORS
    int numComponents() const;
        // Return the total number of components in the system.  Note: This
        // number is the sum of the number of local components and the
        // number of external packages, and is NOT used to calculate ACD
        // and NCCD.

    int numLocalComponents() const;
        // Return the number of (local) components -- i.e., with level > 0.
        // Note: it is this value that is used to calculate ACD and NCCD.

    int numPackages() const;
        // Return the number of entities with a level of 0.  Note a local
        // component that has no external dependencies at all (i.e., not even
        // a standard compiler library include directive) will be incorrectly
        // treated as a package.  Adding a fictitious dependency on the
        // language ("C++") or the local directory (".") corrects this problem.

    int numLevels() const;
        // Return the number of (local) component levels in this subsystem.
        // This value represent the "depth" of the (local) component
        // dependency graph.

    int numCycles() const;
        // Return the number of local cycles in this subsystem

    int numMembers() const;
        // Return the number of cyclically dependent components in this
        // subsystem.

    int ccd() const;
        // Return the Cumulative Component Dependency (CCD) for this subsystem
        // assuming level 0 entities have 0 weight.

    double acd() const;
        // Return the Average Component Dependency (ACD) for this subsystem
        // ignoring level 0 entities.

    double nccd() const;
        // Return the Normalized Cumulative Component Dependency (NCCD) for
        // this subsystem ignoring level 0 entities.

    void printAliases(std::ostream& out) const;
        // Format all aliases in this environment to the specified output
        // stream.

    void printUnaliases(std::ostream& out) const;
        // Format all unaliases in this environment to the specified output
        // stream.

    void printCycles(std::ostream& out) const;
        // Format all cyclically-dependent components to the specified
        // output stream.

    void printLevels(std::ostream& out, int longFlag = 0,
                                   int supressFlag = 0) const;
        // Format all components in levelized order to the specified output
        // stream.  If the optional longFlag argument is specified with a
        // value other than 0, the dependencies of each component will be
        // explicitly delineated.  Otherwise, only the components and their
        // corresponding levels will be included.  By default, component
        // levels and identifying cycle suffixes will be included in the
        // output.  If the value of the optional supressFlag argument is
        // not 0, only the component names will be supplied with levels
        // delimited only by the extra blank line.

    void printSummary(std::ostream& out) const;
        // Format statistics characterizing dependencies within this package
        // to the specified output stream.  These statistics include
        // the following:
        //
        //   Components  The number of (local) components with a level above
        //               0 (i.e., the number of components with at least one
        //               dependency).
        //
        //   Levels      The height of the component dependency graph.
        //
        //   Packages    The number of level 0 entities (i.e., the number of
        //               entities with no dependencies).
        //
        //   CCD         The sum over all (local) components C(i) of the
        //               number of (local) components required to link and
        //               test C(i).
        //
        //   ACD         The ratio of the CCD to the number of (local)
        //               components.
        //
        //   NCCD        The ratio of CCD to the CCD of a (theoretical)
        //               balanced binary dependency tree with an equal
        //               number of local components.  (Note: For most
        //               high-quality package architectures, this number
        //               will not be much greater than 1.00).
        //
        // In the presence of cyclic component dependencies, the members of
        // each distinct maximal cycle are identified with a unique cycle
        // index enclosed in angle brackets ('<' and '>').  An additional
        // summary line preceding the others is formatted to the specified
        // output stream:
        //
        //   Cycles      The number of distinct maximal cycles in the
        //               component dependency graph.
        //
        //   Members     The total number of components participating in
        //               cycles.
};

std::ostream& operator<<(std::ostream& out, const idep_LinkDep& dep);
        // Format all available information in the specified environment (dep)
        // to the specified output stream (out) including the following:
        //   unaliases: directories not to group
        //     aliases: component file name mappings
        //      cycles: maximial interdependent subgraphs
        //      levels: components in levelized order along with dependencies
        //     summary: statistics characterizing local component dependencies

class idep_AliasIter_i;
class idep_AliasIter {
    idep_AliasIter_i *d_this;

  private:
    idep_AliasIter(const idep_AliasIter&);              // not implemented
    idep_AliasIter& operator=(const idep_AliasIter&);   // not implemented

  public:
    // CREATORS
    idep_AliasIter(const idep_LinkDep& linkDep);
    ~idep_AliasIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    const char *fromName() const;
        // Return current alias Name.

    const char *toName() const;
        // Return corresponding actual Name.
};

class idep_UnaliasIter_i;
class idep_UnaliasIter {
    idep_UnaliasIter_i *d_this;

  private:
    idep_UnaliasIter(const idep_UnaliasIter&);              // not implemented
    idep_UnaliasIter& operator=(const idep_UnaliasIter&);   // not implemented

  public:
    // CREATORS
    idep_UnaliasIter(const idep_LinkDep& linkDep);
    ~idep_UnaliasIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    const char *operator()() const;
        // Return current unalias (directory) name.
};

class idep_CycleIter_i;
class idep_CycleIter {
    idep_CycleIter_i *d_this;

    friend class idep_MemberIter;

  private:
    idep_CycleIter(const idep_CycleIter&);              // not implemented
    idep_CycleIter& operator=(const idep_CycleIter&);   // not implemented

  public:
    // CREATORS
    idep_CycleIter(const idep_LinkDep& linkDep);
    ~idep_CycleIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    int weight() const;
        // Return the number of members in the current (maximal) cycle.

    int cycle() const;
        // Return the positive index of the current cycle.
};

class idep_MemberIter_i;
class idep_MemberIter {
    idep_MemberIter_i *d_this;

  private:
    idep_MemberIter(const idep_MemberIter&);            // not implemented
    idep_MemberIter& operator=(const idep_MemberIter&); // not implemented

  public:
    // CREATORS
    idep_MemberIter(const idep_CycleIter& cycleIter);
    ~idep_MemberIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    const char *operator()() const;
        // Return the name of the current member of the current cycle.
};

class idep_LevelIter_i;
class idep_LevelIter {
    idep_LevelIter_i *d_this;

    friend class idep_ComponentIter;

  private:
    idep_LevelIter(const idep_LevelIter&);              // not implemented
    idep_LevelIter& operator=(const idep_LevelIter&);   // not implemented

  public:
    // CREATORS
    idep_LevelIter(const idep_LinkDep& linkDep);
    ~idep_LevelIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    int operator()() const;
        // Return the index of the current level.
};

class idep_ComponentIter_i;
class idep_ComponentIter {
    idep_ComponentIter_i *d_this;

    friend class idep_DependencyIter;

  private:
    idep_ComponentIter(const idep_ComponentIter&);              // not impl.
    idep_ComponentIter& operator=(const idep_ComponentIter&);   // not impl.

  public:
    // CREATORS
    idep_ComponentIter(const idep_LevelIter& levelIter);
    ~idep_ComponentIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    const char *operator()() const;
        // Return the name of the current component on the current level.

    int cycle() const;
        // return the positive index of the current cycle or 0 if acyclic.
};

class idep_DependencyIter_i;
class idep_DependencyIter {
    idep_DependencyIter_i *d_this;

  private:
    idep_DependencyIter(const idep_DependencyIter&);            // not impl.
    idep_DependencyIter& operator=(const idep_DependencyIter&); // not impl.

  public:
    // CREATORS
    idep_DependencyIter(const idep_ComponentIter& componentIter);
    ~idep_DependencyIter();

    // MANIPULATORS
    void operator++();

    // ACCESSORS
    operator const void *() const;
    const char *operator()() const;
        // Return the name of the current component on which the initial
        // component depends.

    int level() const;
        // Return the level of the current component.

    int cycle() const;
        // return the positive index of the current cycle or 0 if acyclic.
};

#endif



